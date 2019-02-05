#ifndef GRAPHVIEW_H
#define GRAPHVIEW_H

#include "fizitem.h"
#include <mainwindow.h>
#include <QMouseEvent>
#include <QMenu>
#include "addelement.h"
#include <QMessageBox>
#include <QPointF>
#include <QVector>
#include <QHash>
#include <QGraphicsProxyWidget>
#include <QTimer>
#include <QWheelEvent>

//Forward-declaration
class FizItem;
class AddElement;
extern QHash<QString, QVector<QVector<FizItem*>>> fizitems;
//Соответствие названия величины и названия ее системной группы
extern QHash<QString, QString> item_group;
//Настройка путей
extern bool change;
//Координаты клика
extern int L_click, T_click;
//Модифицированная сцена
class ModScene : public QGraphicsScene
{
  public:
    explicit ModScene(QWidget *pwrt = nullptr) : QGraphicsScene(pwrt){}
    //Функция для удобного добавления элемента на поле
    FizItem* addFizItem(const int l, const int t, const QColor &col);
};

//Класс для первоначального рисования и инициализации поля (работает в многопоточном режиме)
class InitializeField : public QObject {
    Q_OBJECT
    int line_number;
  public:
    InitializeField(const int &num) :line_number(num){}
public slots:
    void fill_line();
signals:
    void finished();
};

//Класс отображения поля
class GraphView : public QGraphicsView
{
    Q_OBJECT

    friend class InitializeField;
    friend class MainWindow;
    friend class AddElement;
    friend class AddSysGroup;

    QPolygonF polygon;
    int cnt = 0;
    ModScene scene;
    QGraphicsItem *ittt = nullptr;
    QVector<QVector<FizItem*>> out; //Отображаемое поле
    QVector<FizItem*> selected_items; //Список выделенных ячеек
    QMenu *menu = nullptr;
    QMenu *menu_element = nullptr;
    QMenu *level_menu = nullptr;
    FizItem *select = nullptr;

    bool mouseDown = false;
    QPoint lastMousePos;

   public:
    explicit GraphView(QWidget *pwrt = nullptr) : QGraphicsView(pwrt) {
        cnt = 0;
        ittt = nullptr;
        this->setRenderHint(QPainter::Antialiasing);
        scene.setSceneRect(0, 0, 2200, 2000);
        setScene(&scene);
        menu = new QMenu(this);
        menu->addAction(QIcon(":/pics/pics/add.png"), "&Добавить");
        connect(menu, SIGNAL(triggered(QAction*)), SLOT(slotActivated(QAction*)));
    }

    //Создание элемента в логике приложения
    FizItem* create_element(const int &L, const int &T, const int &G, const int &k,
                               const QString &symbol, const QString &name, const QString &sys_c,
                               const QString &uom, const QString &suom, const QString &group,
                               const QColor &color);

    //Удаление элемента в логике приложения
    void remove_element(const QString &name, const int &L, const int &T);
    //!!!ИЗМЕНИТЬ МОДЕЛЬ!!!
    FizItem* AddFizItem(const int &L, const int &T);
    void ClearField();
    void AllUpdate();
    ~GraphView();
protected:
    virtual void contextMenuEvent(QContextMenuEvent *event) override;
    virtual void mouseReleaseEvent(QMouseEvent *event) override;
    virtual void mousePressEvent(QMouseEvent *event) override;
    virtual void mouseMoveEvent(QMouseEvent *event) override;
    virtual void mouseDoubleClickEvent(QMouseEvent *event) override;
    virtual void wheelEvent(QWheelEvent *event) override;
public slots:
    //Отображение действий при нажатии на пункты контекстного меню
    void slotActivated(QAction *act);
    //Выбор блока на других уровнях
    void select_level(QAction *act);

    void zoom(bool in);

    void zoom(double byFactor, QPoint at);
};

#endif // GRAPHVIEW_H
