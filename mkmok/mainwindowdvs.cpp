#include "mainwindowdvs.h"
#include "ui_mainwindowdvs.h"

MainWindowdvs::MainWindowdvs(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindowdvs)
{
    ui->setupUi(this);
}

MainWindowdvs::~MainWindowdvs()
{
    delete ui;
}
