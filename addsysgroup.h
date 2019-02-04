#ifndef ADDSYSGROUP_H
#define ADDSYSGROUP_H

#include <QDialog>
#include "mainwindow.h"
#include <QPalette>
#include <QColorDialog>
#include <QListWidgetItem>

namespace Ui {
class AddSysGroup;
}

class AddSysGroup : public QDialog
{
    Q_OBJECT

public:
    explicit AddSysGroup(QWidget *parent = nullptr);

    ~AddSysGroup();

private slots:
    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_pushButton_4_clicked();

    void on_listWidget_itemClicked(QListWidgetItem *item);

    void on_pushButton_5_clicked();

private:
    Ui::AddSysGroup *ui;
};

#endif // ADDSYSGROUP_H
