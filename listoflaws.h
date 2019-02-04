#ifndef LISTOFLOWS_H
#define LISTOFLOWS_H

#include <QWidget>
#include "lawssettings.h"
#include "mainwindow.h"
#include <QWebEngineView>
extern QString k1, k2, k3, k4; //Четыре величины параллелограмма для связи с формой
extern QString name_law;
extern QString description_law;
extern QString formula_law;
extern QString select_group;


namespace Ui {
class ListOfLaws;
}

class ListOfLaws : public QWidget
{
    Q_OBJECT

public:
    explicit ListOfLaws(QWidget *parent = nullptr);
    ~ListOfLaws();

private slots:
    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_formula_textChanged(const QString &arg1);

protected:
    void closeEvent(QCloseEvent *event);

private:
    Ui::ListOfLaws *ui;
};

#endif // LISTOFLOWS_H
