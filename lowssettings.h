#ifndef LOWSSETTINGS_H
#define LOWSSETTINGS_H

#include <QWidget>
#include "mainwindow.h"
#include <QList>

//Закон
struct Low
{
    QString name; //Название закона
    QString formula; //Формула
    QString description; //Описание закона
    //###### Соотношение (величин)
    QVector<QString> e; // 0-3 (1-4)
    //###########################
    QColor color; //Цвет
    Low(QString &nam, QString formula, QString desc, const QVector<QString> &vec, QColor &col) : name(nam), formula(formula),
       description(desc), e(vec), color(col){}
    Low(){} //Пустой конструктор (для добавления законов из файла)
};

//Перегрузки для записи/считывания законов из файла
QDataStream& operator <<(QDataStream &stream, const Low &low);
QDataStream& operator >>(QDataStream &stream, Low &low);

//Группа законов
struct LowsGroup {
   QColor color; //Цвет, характеризующий данную группу
   QList<Low*> list; //Список законов, принадлежащий данной группе
   LowsGroup(const QColor &col) : color(col){}
   LowsGroup(QColor &col, const QList<Low*> &list) : color(col), list(list){}
};

extern QHash<QString, LowsGroup*> lowsgrouplist; //Список всех групп законов


namespace Ui {
class LowsSettings;
}

class LowsSettings : public QWidget
{
    Q_OBJECT

public:
    explicit LowsSettings(QWidget *parent = nullptr);
    ~LowsSettings();

private slots:
    void on_toolButton_clicked();

    void on_pushButton_clicked();

    void on_color_button_clicked();

    void on_add_button_clicked();

    void on_comboBox_activated(const QString &arg1);

private:
    Ui::LowsSettings *ui;
};

#endif // LOWSSETTINGS_H
