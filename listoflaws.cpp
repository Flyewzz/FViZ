#include "listoflaws.h"
#include "ui_listoflaws.h"

QString k1, k2, k3, k4; //Четыре величины параллелограмма для связи с формой
QString name_law;
QString description_law;
QString formula_law;
QString select_group;

ListOfLaws::ListOfLaws(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::ListOfLaws)
{
    ui->setupUi(this);
    ui->name->setText(name_law);
    ui->description->setText(description_law);
    ui->formula->setText(formula_law);
    //Заполнение полей
    ui->var_1->addItem(k1);
    ui->var_2->addItem(k2);
    ui->var_3->addItem(k3);
    ui->var_4->addItem(k4);
    ui->formulaView->setHtml("<html><head>" + scr + scroll_hide + "</head><body><p align='center'><font size='5'>$$" +
                             QString("{%1}$$").arg(formula_law) + "</font></p></body></html>");
    //################
    foreach (QString group, lawsgrouplist.keys()) {
        ui->groups->addItem(group);
    }
    ui->groups->setCurrentText(select_group); //Выбираем выделенную группу
}

ListOfLaws::~ListOfLaws()
{
    delete ui;
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_law.clear();
    description_law.clear();
    formula_law.clear();
    select_group.clear();

}

void ListOfLaws::on_pushButton_clicked()
{
    QString name = ui->name->text();
    QString description = ui->description->text();
    QString formula = ui->formula->text();
    if (name == "") {
        QMessageBox::critical(this, "Незаполненное поле", "Пожалуйста, заполните название закона!");
        return;
    }
    if ([=]() {
        foreach(Law *law, lawsgrouplist[ui->groups->currentText()]->list) {
            if (name == law->name) {
                return true;
            }
        }
        return false;
    }()) {
        QMessageBox::warning(this, "Дублирование", "В данной группе закон с таким именем уже существует!");
        return;
    }
    QVector<QString> params;
           params << ui->var_1->currentText() << ui->var_2->currentText()
                  << ui->var_3->currentText() << ui->var_4->currentText();
    lawsgrouplist[ui->groups->currentText()]->list << new Law(name, formula, description, params,
                                                        lawsgrouplist[ui->groups->currentText()]->color);
    QMessageBox::information(this, "Добавление закона", "Закон успешно добавлен в систему!");
}

void ListOfLaws::on_pushButton_2_clicked()
{
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_law.clear();
    description_law.clear();
    formula_law.clear();
    select_group.clear();
    this->close();
}

void ListOfLaws::closeEvent(QCloseEvent *event)
{
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_law.clear();
    description_law.clear();
    formula_law.clear();
    select_group.clear();
    QWidget::closeEvent(event);
    this->close();
}

void ListOfLaws::on_formula_textChanged(const QString &arg1)
{
    ui->formulaView->setHtml("<html><head>" + scr + scroll_hide + "</head><body><p align='center'><font size='5'>$$" +
                             QString("{%1}$$").arg(arg1) + "</font></p></body></html>");
}
