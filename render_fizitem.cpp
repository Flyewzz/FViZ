#include "render_fizitem.h"
#include <QDebug>
#include <QString>
#include <QFile>
#include <QJsonDocument>
#include <QStringList>
#include <QTextStream>
#include <QStringLiteral>

// Rendering is performed in QWebEngineView with KaTeX
//
// First, page source is constructed from packed sources in GenHTML
// Then view's HTML is set to generated source
//
// HTML page exposes window.renderFormula, which accepts formula string,
// and sets document.title to TitleDone when formula is rendered.
//
// Task queue with callbacks is used to render formulas one at a time
//
// Public API: task is added with ::Render and cancelled with ::Cancel
//
// Every time ::Fire is called, it calls ProcessTask, which performs
// actual rendering in four steps:
//   1. "renderFormula" is called via runJavaScript
//   2. Formula is rendered
//   3. JS sets title to TitleDone, which ends up calling titleChanged
//   4. In titleChanged pixmap of the view is grabbed and passed to
//   the callback

namespace {

static const auto TitleDone = QStringLiteral("Rendered");

// Utility function to read text file from resources
QString readTextFile(const QString& filename) {
    QFile f(filename);
    if (!f.open(QFile::ReadOnly | QFile::Text)) {
        qDebug() << "Failed to open file" << filename << ":" << f.errorString();
        return QString();
    }
    QTextStream in(&f);
    QString rv = in.readAll();
    f.close();
    return rv;
}

// Utility function to read binary file as base64 string from resources
QString readFileBase64(const QString& filename) {
    QFile f(filename);
    if (!f.open(QFile::ReadOnly)) {
        qDebug() << "Failed to open file" << filename << ":" << f.errorString();
        return QString();
    }
    QString rv(f.readAll().toBase64());
    f.close();
    return rv;
}

// Construct webpage HTML
QString GetHTML() {
    QString fontRegular = readFileBase64(":/katex/KaTeX_Main-Regular.woff");
    QString fontItalic = readFileBase64(":/katex/KaTeX_Main-Italic.woff");

    QString katexCSS = readTextFile(":/katex/katex.css");
    katexCSS
        .replace("%katex_regular_woff%", fontRegular)
        .replace("%katex_italic_woff%", fontItalic);

    QString index = readTextFile(":/katex/index.html");
    QString katexJS = readTextFile(":/katex/katex.js");

    return index
        .replace("%title_done%", TitleDone)
        .replace("%katex_css%", katexCSS)
        .replace("%katex_js%", katexJS);
}
}

RenderFizitem::RenderFizitem(QObject *parent, QWidget *wparent)
    : QObject(parent)
    , _view(new QWebEngineView(wparent))
{
    connect(_view->page(), &QWebEnginePage::titleChanged, this, &RenderFizitem::titleChanged);
    connect(_view->page(), &QWebEnginePage::loadFinished, this, &RenderFizitem::loadFinished);
    _view->setAttribute(Qt::WA_TranslucentBackground);
    _view->page()->setBackgroundColor(Qt::transparent);

    // Unlocked when page is loaded
    _viewLock.lock();
    _view->setHtml(GetHTML());
};

void RenderFizitem::titleChanged(const QString &title) {
    if (title != TitleDone) return;
    // Preserve callback
    const auto callback = _viewTask.callback;
    QPixmap pixmap = _view->grab();
    _viewLock.unlock();
    callback(pixmap);

    Fire();
}

void RenderFizitem::loadFinished(bool) {
    // View is ready for rendering
    _viewLock.unlock();
}

quint64 RenderFizitem::Render(FizItem* item, QSize page_size, double page_scale, callback_t callback) {
    // Schedule task
	Task task;

    task.item = item;
    task.page_size = page_size;
    task.callback = callback;
    task.page_scale = page_scale;

    _lock.lock();
    task.task_id = ++_task_counter;
	_tasks.push_back(task);

    // Schedule Fire if it's not scheduled already
    if (!_firing) {
        _firing = true;
        _lock.unlock();

        QTimer::singleShot(0, this, &RenderFizitem::Fire);
    } else {
        _lock.unlock();
    }

    return task.task_id;
}

bool RenderFizitem::Cancel(quint64 task_id) {
    _lock.lock();
    bool ok = false;

    for (auto it = _tasks.begin(); it != _tasks.end(); ++it) {
        if (it->task_id == task_id) {
            _tasks.erase(it);
            ok = true;
            break;
        }
    }

    _lock.unlock();
    return ok;
}

void RenderFizitem::Fire() {
    // assert(_firing);
    _lock.lock();

    if (_tasks.empty()) {
        // Nothing to process, stop firing
        _firing = false;
        _lock.unlock();
    } else {
        // Fire is called when task is processed
        _firing = true;

        const auto task = _tasks.front();
        _tasks.pop_front();
        _lock.unlock();

        ProcessTask(task);
    }
}

void RenderFizitem::ProcessTask(const Task& task) {
    _viewLock.lock();
    _viewTask = task;

	auto it = task.item;
    // Prepare formula
    auto formula = QString("%1, \\; \\allowbreak %2 \\newline {%3}").arg(
        // Allow breaking on spaces in the name
        QString(it->name).replace(" ", " \\allowbreak "),
        it->symbol,
        it->value_c
    );
    // To avoid JS injection/errors, convert to JSON array with one element
    // (JSON specification doesn't allow strings as root object, so it's necessary to wrap it in array)
    QString formulaJSON(QJsonDocument::fromVariant(QStringList(formula)).toJson(QJsonDocument::Compact));

    // Move view out of window
    _view->move(-100-task.page_size.width(), -100-task.page_size.height());

    // Adjust view for task properties
    _view->resize(task.page_size);
    _view->setZoomFactor(task.page_scale);
    _view->show();

    // Request rendering
    _view->page()->runJavaScript(QString("renderFormula(%1[0])").arg(formulaJSON));
}
