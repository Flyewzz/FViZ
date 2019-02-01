#include "render_fizitem.h"
#include <QDebug>

const static QString loadedTitle = "DONE!!1!";

RenderFizitem::RenderFizitem(QObject *parent, QWidget *wparent)
    : QObject(parent)
    , _view(new QWebEngineView(wparent))
{
    connect(_view->page(), &QWebEnginePage::titleChanged, this, &RenderFizitem::titleChanged);
    _view->show();
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

quint64 RenderFizitem::Render(FizItem* item, QSize page_size, callback_t callback) {
	_lock.lock();
	Task task;
    task.item = item;
    task.page_size = page_size;
    task.callback = callback;
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
        "html,body {"
            "background-color: " + it->level.name() + ";"
            "width: 100%;"
            "height: 100%;"
            "overflow: hidden;"
        "}"
        "</style>"
        "<p align='left'>"
            "<font size='2'>$$" + 
                it->name + ",\\;" + it->symbol + QString("\\\\ {%1} $$").arg(it->value_c) 
            + "</font>"
        "</p>"
        "<script>"
        "document.title = 'notloaded';"
        "MathJax = {"
            "AuthorInit: function(){"
                "MathJax.Hub.Register.StartupHook('End', function(){"
                    "document.title = '" + loadedTitle +"';"
                "});"
            "}"
        "};"
        "</script>"
        "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML\">"
        "</script>"
        "</body>"
    );
    _view->resize(task.page_size);
    _view->update();
}