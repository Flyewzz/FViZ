#include "mainlist.h"
#include "ui_mainlist.h"

void MainList::Fill()
{
    ui->tree->clear();
    //Заполнение раскрывающегося списка (с выделенными законами)
    for (int i = 0; i < ui->listgroups->count(); ++i) {
        //Пропускаем
        if (ui->listgroups->item(i)->checkState() == Qt::Unchecked) continue;
        QString group_name = ui->listgroups->item(i)->text();
        QTreeWidgetItem *item = new QTreeWidgetItem;
        item->setText(0, group_name);
        ui->tree->addTopLevelItem(item);
        foreach (Low *low, lowsgrouplist[group_name]->list) {
            QTreeWidgetItem *child_item = new QTreeWidgetItem;
            child_item->setText(0, low->name);
            item->addChild(child_item);
        }
  }
}

MainList::MainList(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::MainList)
{
    ui->setupUi(this);
    ui->remove_button->setIcon(QIcon(QApplication::style()->standardIcon(QStyle::SP_TrashIcon)));
    //Заполнение общего списка групп законов
    foreach (QString group_name, lowsgrouplist.keys()) {
        QListWidgetItem* it = new QListWidgetItem(group_name, ui->listgroups);
        it->setFlags(it->flags() | Qt::ItemIsUserCheckable); // set checkable flag
        connect(ui->listgroups, &QListWidget::itemChanged, [this](){Fill();});
        it->setCheckState(Qt::Unchecked); // AND initialize check state
    }
    Fill();
    connect(ui->tree, &QTreeWidget::doubleClicked, [=]() {
        //Исправить это условие (добавить обработчик нажатия на группу законов)
        if (ui->tree->currentItem()->parent() != nullptr) {
        //############# Подготовка закона к отображению #########
        //Название группы выделенного закона
        QString group = ui->tree->currentItem()->parent()->text(0);
        //Название выделенного закона
        QString name = ui->tree->currentItem()->text(0);
        select_group = group; //Устанавливаем группу
        name_low = name;
        Low *find_low = [=]() {
            foreach (Low *low, lowsgrouplist[select_group]->list) {
                if (low->name == name_low)
                    return low;
            }
        }();
        description_low = find_low->description;
        formula_low = find_low->formula;
        k1 = find_low->e[0]; k2 = find_low->e[1];
        k3 = find_low->e[2]; k4 = find_low->e[3];
        //#######################################################
        //Отображение закона
        ListOfLows *w = new ListOfLows;
        w->show();
      }
    });
}

MainList::~MainList()
{
    delete ui;
}

void MainList::on_checkBox_clicked(bool checked)
{
    if (checked)
        for (int i = 0; i < ui->listgroups->count(); ++i) {
            ui->listgroups->item(i)->setCheckState(Qt::Checked);
        }
    else
        for (int i = 0; i < ui->listgroups->count(); ++i) {
            ui->listgroups->item(i)->setCheckState(Qt::Unchecked);
        }
    Fill();
}
