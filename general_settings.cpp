#include "general_settings.h"
#include "ui_general_settings.h"

General_Settings::General_Settings(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::General_Settings)
{
    ui->setupUi(this);
    this->setGeometry(400,0,400,490);
    i_c = 0;
    timer = new QTimer(this);
    connect(timer, &QTimer::timeout, [&]() {
        this->setGeometry(main_window->pos().x()+i_c*2, main_window->pos().y(),400,490);
        if(++i_c > 400) timer->stop();
    });
    timer->start(3);
}

General_Settings::~General_Settings()
{
    delete ui;
}
