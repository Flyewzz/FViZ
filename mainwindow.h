#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QString>
#include <QGraphicsView>
#include <QPushButton>
#include "graphview.h"
#include <QScrollBar>
#include <QToolBar>
#include "about.h"
#include <QLabel>
#include "addsysgroup.h"
#include "listoflaws.h"
#include "lawssettings.h"
#include "mainlist.h"
#include <QMessageBox>
#include <QWebEngineView>
#include <QWebEngineSettings>
#include <QIcon>
#include <QFile>
#include <QDataStream>
#include <QFileDialog>
#include <QPixmap>
#include <QDir>
#include <QDebug>
#include <QCursor>
#include "fizitem.h"
#include "commands.h"
#include <QPropertyAnimation>
#include "render_fizitem.h"

class FizItem;
extern QString scr;
extern QString scroll_hide;
extern int choose;
extern int gL, gT;
extern int N; //Размеры рабочей области (LT)
extern QLabel *position;
extern QLabel *Gk;
extern QLabel *name_izm;
//Файл для взаимодействия с базой данных элементов
extern QFile work_file;
//Файловый поток ввода-вывода
extern QDataStream work_stream;
//Путь до рабочего файла
extern QString work_str;
extern QAction *undo_action;
extern QAction *redo_action;
class RenderFizitem;
extern RenderFizitem *renderer;

extern QMainWindow *main_window;
//Описание системной группы ФВ
struct SysGroup {
 int G;
 int k;
 QColor color;
 SysGroup(const int &a, const int &b, const QColor &c) : G(a), k(b), color(c){}
};

//Для удобства обращения с файловым потоком
QDataStream& operator << (QDataStream &stream, const SysGroup &elem);
QDataStream& operator >> (QDataStream &stream, SysGroup &elem);

//Создание новой системной группы (с выделением памяти под весь слой на данном уровне)
void CreateSysGroup(const QString &name, const int &G, const int &k, const QColor &col = Qt::black);
//Удаление системной группы (с очисткой памяти всего слоя на данном уровне)
void RemoveSysGroup(const QString &name);

void EditSysGroup(QString old_name, QString new_name, const int &G, const int &k, const QColor &col = Qt::black);

//Хэш параметры системных групп ФВ
extern QHash<QString, SysGroup*> sysgroup;

//Forward-declaration
class GraphView;

extern GraphView *main_view;
namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT
    void ClearStruct(); //Процедура полной очистки памяти программы
    void Save(); //Функция сохранения сцены в файл
    void Open(); //Функция выгрузки сцены из файла
    void CreateActions();
public:
    explicit MainWindow(QWidget *parent = nullptr);
    void BuildLevel(const int &);
    ~MainWindow();
protected:
    virtual void closeEvent(QCloseEvent *event);
private slots:
    void on_action_2_triggered();

    void on_action_3_triggered();

    void on_action_6_triggered();

    void on_action_10_triggered();

    void on_action_9_triggered();

    void on_action_12_triggered();

    void on_action_5_triggered();

    void on_action_11_triggered();

    void on_action_8_triggered();

    void on_MainWindow_destroyed();

    void on_action_7_triggered();

    void on_undoAction_triggered();
    void on_redoAction_triggered();

    void on_zoomInAction_triggered();
    void on_zoomOutAction_triggered();

private:
    Ui::MainWindow *ui;
};
#endif // MAINWINDOW_H
