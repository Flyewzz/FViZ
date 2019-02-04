#ifndef MAINLIST_H
#define MAINLIST_H

#include <QDialog>
#include <QTreeWidget>
#include <QTreeWidgetItem>
#include <QCheckBox>
#include "lawssettings.h"

namespace Ui {
class MainList;
}

class MainList : public QDialog
{
    Q_OBJECT
    void Fill(); //Заполнение раскрывающегося списка
public:
    explicit MainList(QWidget *parent = nullptr);
    ~MainList();

private slots:
    void on_checkBox_clicked(bool checked);

private:
    Ui::MainList *ui;
};

#endif // MAINLIST_H
