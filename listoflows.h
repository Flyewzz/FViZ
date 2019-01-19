#ifndef LISTOFLOWS_H
#define LISTOFLOWS_H

#include <QWidget>
#include "lowssettings.h"
#include "mainwindow.h"
#include <QWebEngineView>
extern QString k1, k2, k3, k4; //Четыре величины параллелограмма для связи с формой
extern QString name_low;
extern QString description_low;
extern QString formula_low;
extern QString select_group;


namespace Ui {
class ListOfLows;
}

class ListOfLows : public QWidget
{
    Q_OBJECT

public:
    explicit ListOfLows(QWidget *parent = nullptr);
    ~ListOfLows();

private slots:
    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_formula_textChanged(const QString &arg1);

protected:
    void closeEvent(QCloseEvent *event);

private:
    Ui::ListOfLows *ui;
};

#endif // LISTOFLOWS_H
