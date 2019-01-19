#include "addsysgroup.h"
#include "ui_addsysgroup.h"

QColor color;


AddSysGroup::AddSysGroup(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::AddSysGroup)
{
    ui->setupUi(this);
    ui->color_value->setAutoFillBackground(true); // Обязательно
    QPalette palette;
    palette.setColor(QPalette::Background, Qt::black);
    ui->color_value->setPalette(palette);
    //Отображаем все системные группы в виде списка
    foreach (QString line, sysgroup.keys()) {
      ui->listWidget->addItem(line);
    }
}

AddSysGroup::~AddSysGroup()
{
    delete ui;
}

void AddSysGroup::on_pushButton_clicked()
{
    if (sysgroup.empty()) {
        QMessageBox::warning(this, "Удаление", "Список пуст!");
        return;
    }
    //Удаляем все выделенные группы
    foreach(QListWidgetItem *it,
            ui->listWidget->selectedItems()) {
        RemoveSysGroup(it->text());
        delete it;
    }
}

void AddSysGroup::on_pushButton_2_clicked()
{
    QString name_sysgroup = ui->lineEdit->text();
    //Добавление системной группы
    if (name_sysgroup == "") {
        QMessageBox::warning(this, "Пустое поле", "Пожалуйста, заполните поле для названия системной группы!");
        return;
    }
    if (!ui->listWidget->selectedItems().empty()) {
        EditSysGroup(ui->listWidget->currentItem()->text(), name_sysgroup,
                     ui->g_coord->value(), ui->k_coord->value(), color);
        ui->listWidget->currentItem()->setText(name_sysgroup);
        for (QVector<FizItem*> line : main_view->out) {
            for (FizItem *select : line) {
                if (select->name == "" || !select->visible) {
                    continue;
                }
                FizItem *item = fizitems[item_group.value(select->name)][select->T+N/2][select->T+select->L+N-6];
                select->level = item->level;
                select->name = item->name;
                select->G = item->G;
                select->k = item->k;
                select->symbol = item->symbol;
                select->unit_of_measurement = item->unit_of_measurement;
                select->symbol_unit_of_measurement = item->symbol_unit_of_measurement;
                select->getTex()->page()->setBackgroundColor(select->level);
                select->getTex()->setHtml("<html><head>" + scr + scroll_hide + "</head><body><p align='left'><font size='2'>$$" +
                                          select->name + ",\\;" + select->symbol +
                                     QString("\\\\ {%1} $$").arg(select->value_c) + "</font></p></body></html>");
//                select->getTex()->setVisible(true);
                select->update();
            }
        }
        main_view->AllUpdate();
        qDebug() << "FizItems:";
        for (QString group  : fizitems.keys()) {
            qDebug() << "Группа " + group + ":";
            for (QVector<FizItem*> field : fizitems[group]) {
                for (FizItem *item : field) {
                    qDebug() << item->getName();
                }
            }
        }

        qDebug() << "Поле:";
        for (QVector<FizItem*> line : main_view->out) {
            for (FizItem *item : line) {
                qDebug() << item->getName() + " : " + item_group[item->getName()];
            }
        }
        return;
    }
    if ([=]() {
            foreach (QString line, sysgroup.keys()) {
                if (name_sysgroup == line) {
                    return true;
                }
            }
            return false;
}()) {
        QMessageBox::warning(this, "Дублирование", "Системная группа с таким названием уже существует!");
        ui->listWidget->addItem(name_sysgroup);
        ui->lineEdit->clear();
        ui->lineEdit->setFocus();
    }
    CreateSysGroup(name_sysgroup, ui->g_coord->value(), ui->k_coord->value(), color);
    ui->listWidget->addItem(name_sysgroup);
    ui->listWidget->sortItems(); //Сортируем системные группы по алфавиту в порядке возрастания
    ui->lineEdit->clear();
    ui->lineEdit->setFocus();
}

void AddSysGroup::on_pushButton_4_clicked()
{
    //Изменение цвета новой системной группы
    QColor temp;
    temp = QColorDialog::getColor(temp, nullptr, tr("Цвет контура"));
    if (temp.isValid())
    {
        color = temp;
        QPalette palette;
        palette.setColor(QPalette::Background, color);
        ui->color_value->setPalette(palette);
    }
}

void AddSysGroup::on_listWidget_itemClicked(QListWidgetItem *item)
{
    QString name_sysgroup = item->text();
    ui->lineEdit->setText(name_sysgroup);
    color = sysgroup[name_sysgroup]->color;
    QPalette palette;
    palette.setColor(QPalette::Background, color);
    ui->color_value->setPalette(palette);
    ui->g_coord->setValue(sysgroup[name_sysgroup]->G);
    ui->k_coord->setValue(sysgroup[name_sysgroup]->k);
}

void AddSysGroup::on_pushButton_5_clicked()
{
        ui->listWidget->clearSelection();
        ui->lineEdit->clear();
        color = Qt::black;
        QPalette palette;
        palette.setColor(QPalette::Background, color);
        ui->color_value->setPalette(palette);
        ui->lineEdit->setFocus();
}
