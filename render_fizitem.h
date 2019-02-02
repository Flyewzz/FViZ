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

using callback_t = std::function<void (const QPixmap&)>;

quint64 Render(FizItem* item, QSize page_size, callback_t callback);
bool Cancel(quint64 task_id);
void Fire();

private:
struct Task {
	FizItem* item = nullptr;
	QSize page_size{};
	callback_t callback = nullptr;
	quint64 task_id = 0;
};
void ProcessTask(const Task& task);
void titleChanged(const QString &title);

QList<Task> _tasks{};
QMutex _lock{};
quint64 _task_counter = 0;
bool firing = true;

QWebEngineView* _view = nullptr;
QMutex _viewLock{};
Task _viewTask{};
};

#endif
