#include "about.h"
#include "ui_about.h"

About::About(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::About)
{
    ui->setupUi(this);
    ui->label_4->setOpenExternalLinks(true);
    ui->label_5->setOpenExternalLinks(true);
}

About::~About()
{
    delete ui;
}
