#ifndef ADDELEMENT_H
#define ADDELEMENT_H

#include <QDialog>
#include "mainwindow.h"
#include <QPalette>
#include <QWebEngineView>

//Флаг изменения (1 - если изменяем уже существующий элемент, 0 - если добавляем новый)
extern bool change_elem;

namespace Ui {
class AddElement;
}

//Форма для добавления нового элемента
class AddElement : public QDialog
{
    Q_OBJECT

public:
    explicit AddElement(QWidget *parent = nullptr);
    ~AddElement();

private slots:
    void on_pushButton_clicked();

    void on_comboBox_activated(const QString &arg1);

    void on_pushButton_2_clicked();

private:
    Ui::AddElement *ui;
};

#endif // ADDELEMENT_H
