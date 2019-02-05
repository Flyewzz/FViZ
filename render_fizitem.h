#ifndef RENDER_FIZITEM_H
#define RENDER_FIZITEM_H

#include <functional>
#include <QPainter>
#include <QColor>
#include <QPixmap>
#include <QList>
#include <QWebEngineView>
#include <QMutex>
#include <QSize>
#include "fizitem.h"

class RenderFizitem: public QObject {
Q_OBJECT

public:

RenderFizitem(): RenderFizitem(static_cast<QObject*>(nullptr)){}
RenderFizitem(QObject *parent): RenderFizitem(parent, nullptr){}
RenderFizitem(QObject *parent, QWidget *wparent);

~RenderFizitem() {
	delete _view;
}

// Callback for render task
using callback_t = std::function<void (const QPixmap&)>;

// Add render task with callback, get cancel token (task_id)
quint64 Render(FizItem* item, QSize page_size, double page_scale, callback_t callback);
// Cancel task by token (task_id)
bool Cancel(quint64 task_id);

// Start processing tasks
void Fire();

private:
struct Task {
	FizItem* item = nullptr;
	QSize page_size{};
	double page_scale = 1;
	callback_t callback = nullptr;
	quint64 task_id = 0;
};
// Process single task
void ProcessTask(const Task& task);

private slots:
void loadFinished(bool);
void printRequested();

private:
// _tasks, _task_counter and _firing lock
QMutex _lock{};
// Known task list
QList<Task> _tasks{};
// Counter for task ID
quint64 _task_counter = 0;
// True if Fire scheduled
bool _firing = false;

// _view and _viewTask lock
QMutex _viewLock{};
// WebView for rendering
QWebEngineView* _view = nullptr;
// Task being rendered
Task _viewTask{};
};

#endif
