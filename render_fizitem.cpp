#include "render_fizitem.h"
#include <QDebug>

const static QString loadedTitle = "DONE!!1!";

RenderFizitem::RenderFizitem(QObject *parent, QWidget *wparent)
    : QObject(parent)
    , _view(new QWebEngineView(wparent))
{
    connect(_view->page(), &QWebEnginePage::titleChanged, this, &RenderFizitem::titleChanged);
    _view->setAttribute(Qt::WA_TranslucentBackground);
    _view->page()->setBackgroundColor(Qt::transparent);
};

void RenderFizitem::titleChanged(const QString &title) {
    if (title == loadedTitle) {
        const auto callback = _viewTask.callback;
        QPixmap pixmap = _view->grab();
        _viewLock.unlock();
        callback(pixmap);

        Fire();
    }
}

quint64 RenderFizitem::Render(FizItem* item, QSize page_size, double page_scale, callback_t callback) {
	Task task;

    task.item = item;
    task.page_size = page_size;
    task.callback = callback;
    task.page_scale = page_scale;

    _lock.lock();
    task.task_id = ++_task_counter;
	_tasks.push_back(task);

    if (!firing) {
        firing = true;
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
    _lock.lock();

    if (_tasks.empty()) {
        firing = false;
        _lock.unlock();
    } else {
        firing = true;
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

    _view->setHtml(
        "<body>"
        "<style>"
        "html, body {"
            "background: transparent;"
            "width: 100%;"
            "height: 100%;"
            "margin: 0px;"
            "position: absolute;"
            "overflow: hidden;"
            "display: flex;"
            "justify-content: center;"
            "align-items: center;"
        "}"
        "</style>"
        "<div id=\"formula_container\">"
            +QString("$$ %1,\\;%2\\\\ {%3} $$").arg(it->name, it->symbol, it->value_c)+
        "</p>"
        "<script>"
        "document.title = 'notloaded';"
        "MathJax = {"
            "AuthorInit: function(){"
                "MathJax.Hub.Register.StartupHook('End', function(){"
                    "MathJax.Hub.Queue(['Typeset', MathJax.Hub, 'formula_container'], function(){"
                        "document.title = '" + loadedTitle +"';"
                    "});"
                "});"
            "}"
        "};"
        "</script>"
        "<script type=\"text/x-mathjax-config\">"
            "MathJax.Hub.Config({"
                "messageStyle: 'none',"
                "CommonHTML: { linebreaks: { automatic: true }, scale: "+QString::number(task.page_scale*100)+"},"
                "\"HTML-CSS\": { linebreaks: { automatic: true }, scale: "+QString::number(task.page_scale*100)+"},"
                "SVG: { linebreaks: { automatic: true }, scale: "+QString::number(task.page_scale*100)+"},"
            "});"
        "</script>"
        "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML\">"
        "</script>"
        "</body>"
    );
    _view->move(-100-task.page_size.width(), -100-task.page_size.height());
    _view->resize(task.page_size);
    _view->show();
    _view->update();
}