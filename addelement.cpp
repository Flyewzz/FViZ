#include "addelement.h"
#include "ui_addelement.h"

QColor choose_color;
//Флаг изменения (1 - если изменяем уже существующий элемент, 0 - если добавляем новый)
bool change_elem;

FizItem *remember_element;

AddElement::AddElement(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::AddElement)
{
    ui->setupUi(this);
    ui->color_value->setAutoFillBackground(true); // Обязательно
    foreach (QString group, sysgroup.keys()) {
        ui->comboBox->addItem(group);
    }
    QPalette palette;
    if (sysgroup.empty()) {
        palette.setColor(QPalette::Background, Qt::black);
        choose_color = Qt::black;
        ui->pushButton->setEnabled(false);
       // ui->pushButton->setCursor(Qt::ForbiddenCursor);
        ui->nameval->setEnabled(false);
        ui->uom->setEnabled(false);
        ui->symbol->setEnabled(false);
        ui->suom->setEnabled(false);
        ui->sys_c->setEnabled(false);
        ui->l_coord->setEnabled(false);
        ui->t_coord->setEnabled(false);
    }
    else {
      //  ui->pushButton->setCursor(Qt::ArrowCursor);
        choose_color = sysgroup[ui->comboBox->currentText()]->color;
        palette.setColor(QPalette::Background, choose_color);
        ui->g_coord->setText(QString::number(sysgroup[ui->comboBox->currentText()]->G, 'g', 10));
        ui->k_coord->setText(QString::number(sysgroup[ui->comboBox->currentText()]->k, 'g', 10));
    }
    //Заносим координаты клика
    ui->l_coord->setValue(L_click);
    ui->t_coord->setValue(T_click);
    if (change_elem) {
        remember_element = main_view->out[T_click+N/2][T_click+L_click+N/2];
        FizItem *&item = remember_element;
        ui->g_coord->setText(QString::number(item->G, 'g', 10));
        ui->k_coord->setText(QString::number(item->k, 'g', 10));
        ui->symbol->setText(item->symbol);
        ui->nameval->setText(item->name);
        ui->sys_c->setText(item->value_c);
        ui->uom->setText(item->unit_of_measurement);
        ui->suom->setText(item->symbol_unit_of_measurement);
        ui->comboBox->setCurrentText(item_group[item->name]);
        choose_color = item->level;
        palette.setColor(QPalette::Background, choose_color);
    }

    ui->color_value->setPalette(palette);
}

AddElement::~AddElement()
{
    delete ui;
    L_click = T_click = 0; //Сбрасываем указатель LT
}

void AddElement::on_pushButton_clicked()
{
    if (ui->nameval->text() == "") {
        QMessageBox::warning(this, "Незаполненное поле", "Заполните поле для названия величины!");
        return;
    }
    if (!change_elem) { //Дубликация может быть только в случае создания нового элемента
        if (item_group.contains(ui->nameval->text())) {
            ui->nameval->clear();
            ui->nameval->setFocus();
            QMessageBox::warning(this, "Дубликация величин", "Такая величина уже существует!");
            return;
         }
    }
    //Считывание значений из полей ввода
    int L = ui->l_coord->value();
    int T = ui->t_coord->value();
    int G = ui->g_coord->text().toInt();
    int k = ui->k_coord->text().toInt();
    QString symbol = ui->symbol->text();
    QString name = ui->nameval->text();
    QString sys_c = ui->sys_c->text();
    QString uom = ui->uom->text();
    QString suom = ui->suom->text();
    QString group = ui->comboBox->currentText();
    if (change_elem) {
        QString remember_name = remember_element->name; //Имя нажатого элемента
        int remember_G = remember_element->G;
        int remember_k = remember_element->k;
        QString remember_symbol = remember_element->symbol;
        QString remember_sys_c = remember_element->value_c;
        QString remember_uom = remember_element->unit_of_measurement;
        QString remember_suom = remember_element->symbol_unit_of_measurement;
        QString remember_group = item_group[remember_element->name];
        QColor remember_color = remember_element->level;
        //main_view->out[T_click+N/2][T_click+L_click+N/2]->RemoveCell();
        main_view->remove_element(remember_element->name, L_click, T_click);
        remember_element = main_view->create_element(L, T, G, k,
                                  symbol, name, sys_c,
                                  uom, suom, group, choose_color);
        undo << new Command_Element(L_click, T_click,
                                    remember_G, remember_k,
                                    remember_symbol, remember_name,
                                    remember_sys_c,
                                    remember_uom,
                                    remember_suom,
                                    remember_group,
                                    remember_color, 0, 0, remember_element);
        goto change_element_continue;
    }
    main_view->create_element(L, T, G, k,
                              symbol, name, sys_c,
                              uom, suom, group, choose_color);
    undo << new Command_Element(L, T, G, k, symbol, name, sys_c,
                                    uom, suom, group, choose_color);
    change_element_continue:
    L_click = L;
    T_click = T;
    undo_action->setEnabled(true);
    foreach (Command *command, redo) {
        delete command;
    }
    redo.clear();
    redo_action->setEnabled(false);
    QMessageBox::information(this, "Физическая величина", "Величина успешно внесена в таблицу!");
}

void AddElement::on_comboBox_activated(const QString &arg1)
{
    ui->g_coord->setText(QString::number(sysgroup[arg1]->G, 'g', 10));
    ui->k_coord->setText(QString::number(sysgroup[arg1]->k, 'g', 10));
    choose_color = sysgroup[arg1]->color;
    QPalette palette;
    palette.setColor(QPalette::Background, choose_color);
    ui->color_value->setPalette(palette);
}

void AddElement::on_pushButton_2_clicked()
{
    L_click = T_click = 0; //Сбрасываем указатель LT
    this->close(); //Закрываем форму
}
