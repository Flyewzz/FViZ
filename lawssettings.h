#ifndef LOWSSETTINGS_H
#define LOWSSETTINGS_H

#include <QWidget>
#include "mainwindow.h"
#include <QList>

//Закон
struct Law
{
    QString name; //Название закона
    QString formula; //Формула
    QString description; //Описание закона
    //###### Соотношение (величин)
    QVector<QString> e; // 0-3 (1-4)
    //###########################
    QColor color; //Цвет
    Law(QString &nam, QString formula, QString desc, const QVector<QString> &vec, QColor &col) : name(nam), formula(formula),
       description(desc), e(vec), color(col){}
    Law(){} //Пустой конструктор (для добавления законов из файла)
};

//Перегрузки для записи/считывания законов из файла
QDataStream& operator <<(QDataStream &stream, const Law &law);
QDataStream& operator >>(QDataStream &stream, Law &law);

//Группа законов
struct LawsGroup {
   QColor color; //Цвет, характеризующий данную группу
   QList<Law*> list; //Список законов, принадлежащий данной группе
   LawsGroup(const QColor &col) : color(col){}
   LawsGroup(QColor &col, const QList<Law*> &list) : color(col), list(list){}
};

extern QHash<QString, LawsGroup*> lawsgrouplist; //Список всех групп законов


namespace Ui {
class LawsSettings;
}

class LawsSettings : public QWidget
{
    Q_OBJECT

public:
    explicit LawsSettings(QWidget *parent = nullptr);
    ~LawsSettings();

private slots:
    void on_toolButton_clicked();

    void on_pushButton_clicked();

    void on_color_button_clicked();

    void on_add_button_clicked();

    void on_comboBox_activated(const QString &arg1);

private:
    Ui::LawsSettings *ui;
};

#endif // LOWSSETTINGS_H
