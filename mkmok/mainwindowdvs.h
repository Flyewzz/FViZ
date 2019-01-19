#ifndef MAINWINDOWDVS_H
#define MAINWINDOWDVS_H

#include <QMainWindow>

namespace Ui {
class MainWindowdvs;
}

class MainWindowdvs : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindowdvs(QWidget *parent = 0);
    ~MainWindowdvs();

private:
    Ui::MainWindowdvs *ui;
};

#endif // MAINWINDOWDVS_H
