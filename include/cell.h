#ifndef CELL_H
#define CELL_H

#include <string>

using std::string;

//Описание одного блока
class Cell
{
    std::string _name; //Название блока
    string _symbol; //Условное обозначение
    string _unit_of_measurement; //Единица измерения
    string _symbol_unit_of_measurement; //Обозначение единицы измерения
    int L; //Координата пути
    int T; //Координата времени
    string _value_c; // Размерность в СИ

public:
    explicit Cell();
    ~Cell();

    string getName() const {
        return _name;
    }

};

#endif // CELL_H
