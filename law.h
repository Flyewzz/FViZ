#ifndef LOWSSETTINGS_H
#define LOWSSETTINGS_H

#include <string>
#include <array>

#include "cell.h"

using std::string;
using std::array;

//Закон
class LawC
{
    string name; //Название закона
    string formula; //Формула
    string description; //Описание закона
    //###### Соотношение (величин)
    array<Cell*, 4> _e; // 0-3 (1-4)
    //###########################
//    QColor color; //Цвет
    Law(string &nam, string formula, string desc, const QVector<string> &vec, QColor &col) : name(nam), formula(formula),
       description(desc), e(vec), color(col){}
    Law(){} //Пустой конструктор (для добавления законов из файла)
};
