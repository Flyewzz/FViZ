#ifndef COMMANDS_H
#define COMMANDS_H

/******************
 * ######### Описание модуля #########
 * Данная часть предназначена для управления командами приложения
 * Здесь реализованы два стека (один для хранения операций, другой для хранения операций отмены)
 * Commands - это абстрактный класс, который описывает одну команду в целом (абстрактную команду)
 * У него есть несколько реализаций, которые умеют по-особенному обрабатывать различные команды
 * ######### Описание действий классов #########
 * Первоначальная идея такова: Пользователь выполняет различные операции (добавление/удаление/изменение)
 * над сотами, системными группами, законами и их группами и т.д.
 * Изменения, которые он совершает, мы можем представить в виде совокупности команд, которые
 * будут отслеживаться в приложении. Commands будет содержать флаг, который будет определять,
 * что должна делать отмена - что-то удалять или что-то возвращать.
 * То есть, к примеру, если мы добавляем соту (меняем флаг на 0 - flag = 0), и при нажатии Ctrl+Z
 * излекаем операцию из стека с флагом 0 (что означает, что мы должны выполнить команду удаления -
 * команду, обратную сделанной). Наоборот: мы что-то удаляем, флаг меняется на 1, значит,
 * чтобы это "что-то" вернуть, нужно восстановить удаленный объект, т.е. выполнить его создание.
 * ######### Классы #########
 * Commands - абстрактный класс для описания любой команды
 */

#include <QStack>
#include "mainwindow.h"

//Forward-declaration
class Command;
class FizItem;

//Стеки общего уровня для хранения команд (отмены и повтора)
extern QStack<Command*> undo;
extern QStack<Command*> redo;

//Общий абстрактный класс, описывающий одну команду
class Command
{
protected:
    int id;
    int flag; //Флаг добавления/изменения/удаления (1 - add, 0 - change, -1 - remove)
public:
    virtual QString createLogs() = 0;
    virtual void execute() = 0;
    virtual ~Command(){} //Виртуальный деструктор
    int getId();
};

class Command_Element : public Command {
    int L;
    int T;
    int G;
    int k;
    QString symbol;
    QString name;
    QString sys_c;
    QString uom;
    QString suom;
    QString group;
    QColor color;
    FizItem *_item;
public:
    explicit Command_Element(const int &L, const int &T, const int &G, const int &k,
                             const QString &symbol, const QString &name, const QString &sys_c,
                             const QString &uom, const QString &suom, const QString &group,
                             const QColor &color, const int &flag = -1, const int &id = 0,
                             FizItem *it = nullptr) : L(L), T(T), G(G), k(k),
                             symbol(symbol), name(name), sys_c(sys_c), uom(uom), suom(suom),
                             group(group), color(color), _item(it) {this->flag = flag; this->id = id;}
    void setId(const int &num = 1) {id = num;} //Изначально в первом стеке (undo), 1 = redo
    QString createLogs();
    void execute();
};

#endif // COMMANDS_H
