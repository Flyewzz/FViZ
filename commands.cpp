#include "commands.h"
//Состояния флага
enum FlagState {REMOVE = -1, CHANGE, ADD};

namespace {
//Стеки общего уровня для хранения команд (отмены и повтора)
QMutex commandStacksLock;
QStack<Command*> undo;
QStack<Command*> redo;

void SyncUI() {
    undo_action->setEnabled(!undo.empty());
    redo_action->setEnabled(!redo.empty());
}

} // anonymous namespace

void AddUndoCommand(Command* cmd) {
    commandStacksLock.lock();

    if (cmd != nullptr) {
        undo << cmd;

        for (const auto redoCmd : redo) {
            delete redoCmd;
        }

        redo.clear();
    }

    SyncUI();

    commandStacksLock.unlock();
}

void AddRedoCommand(Command* cmd) {
    commandStacksLock.lock();

    if (cmd != nullptr) {
        redo << cmd;
    }
    SyncUI();

    commandStacksLock.unlock();
}

Command* PopUndoCommand() {
    commandStacksLock.lock();

    Command *cmd = nullptr;
    if (!undo.empty()) {
        cmd = undo.pop();
    }
    SyncUI();

    commandStacksLock.unlock();
    return cmd;
}

Command* PopRedoCommand() {
    commandStacksLock.lock();

    Command *cmd = nullptr;
    if (!redo.empty()) {
        cmd = redo.pop();
    }
    SyncUI();

    commandStacksLock.unlock();
    return cmd;
}

QString Command_Element::createLogs()
{
    return "Лог 1";
}


void Command_Element::execute()
{
    if (id == 0) {
        if (flag == FlagState::ADD) {
            main_view->create_element(L, T, G, k,
                                  symbol, name, sys_c,
                                  uom, suom, group, color);
            AddRedoCommand(new Command_Element(L, T, G, k,
                                    symbol, name, sys_c,
                                    uom, suom,
                                    item_group[name], color, -1, 1));
    }
    else if  (flag == FlagState::REMOVE) {
        AddRedoCommand(new Command_Element(L, T, G, k,
                                    symbol, name, sys_c,
                                    uom, suom,
                                    item_group[name], color, 1, 1));
        main_view->remove_element(name, L, T);
    }
    else if (flag == FlagState::CHANGE) {
            QString remember_name = _item->name; //Имя нажатого элемента
            int remember_L = _item->L;
            int remember_T = _item->T;
            int remember_G = _item->G;
            int remember_k = _item->k;
            QString remember_symbol = _item->symbol;
            QString remember_sys_c = _item->value_c;
            QString remember_uom = _item->unit_of_measurement;
            QString remember_suom = _item->symbol_unit_of_measurement;
            QString remember_group = item_group[_item->name];
            QColor remember_color = _item->level;
            main_view->remove_element(_item->name, _item->L, _item->T);
            _item = main_view->create_element(L, T, G, k,
                                  symbol, name, sys_c,
                                  uom, suom, group, color);
            AddRedoCommand(new Command_Element(remember_L, remember_T,
                                    remember_G, remember_k,
                                    remember_symbol, remember_name,
                                    remember_sys_c,
                                    remember_uom,
                                    remember_suom,
                                    remember_group,
                                    remember_color, 0, 1, _item));
    }
    return;
    }
    if (flag == FlagState::ADD) {
            main_view->create_element(L, T, G, k,
                                      symbol, name, sys_c,
                                      uom, suom, group, color);
            AddUndoCommand(new Command_Element(L, T, G, k,
                                        symbol, name, sys_c,
                                        uom, suom,
                                        item_group[name], color, -1));
        }
        else if  (flag == FlagState::REMOVE) {
            AddUndoCommand(new Command_Element(L, T, G, k,
                                        symbol, name, sys_c,
                                        uom, suom,
                                        item_group[name], color, 1));
            main_view->remove_element(name, L, T);
        }
        else if (flag == FlagState::CHANGE) {
            QString remember_name = _item->name; //Имя нажатого элемента
            int remember_L = _item->L;
            int remember_T = _item->T;
            int remember_G = _item->G;
            int remember_k = _item->k;
            QString remember_symbol = _item->symbol;
            QString remember_sys_c = _item->value_c;
            QString remember_uom = _item->unit_of_measurement;
            QString remember_suom = _item->symbol_unit_of_measurement;
            QString remember_group = item_group[_item->name];
            QColor remember_color = _item->level;
            main_view->remove_element(_item->name, _item->L, _item->T);
            _item = main_view->create_element(L, T, G, k,
                              symbol, name, sys_c,
                              uom, suom, group, color);
            AddUndoCommand(new Command_Element(remember_L, remember_T,
                                remember_G, remember_k,
                                remember_symbol, remember_name,
                                remember_sys_c,
                                remember_uom,
                                remember_suom,
                                remember_group,
                                remember_color, 0, 0, _item));
        }
}
