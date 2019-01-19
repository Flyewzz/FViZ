#include "listoflows.h"
#include "ui_listoflows.h"

QString k1, k2, k3, k4; //Четыре величины параллелограмма для связи с формой
QString name_low;
QString description_low;
QString formula_low;
QString select_group;

ListOfLows::ListOfLows(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::ListOfLows)
{
    ui->setupUi(this);
    ui->name->setText(name_low);
    ui->description->setText(description_low);
    ui->formula->setText(formula_low);
    //Заполнение полей
    ui->var_1->addItem(k1);
    ui->var_2->addItem(k2);
    ui->var_3->addItem(k3);
    ui->var_4->addItem(k4);
    ui->formulaView->setHtml("<html><head>" + scr + scroll_hide + "</head><body><p align='center'><font size='5'>$$" +
                             QString("{%1}$$").arg(formula_low) + "</font></p></body></html>");
    //################
    foreach (QString group, lowsgrouplist.keys()) {
        ui->groups->addItem(group);
    }
    ui->groups->setCurrentText(select_group); //Выбираем выделенную группу
}

ListOfLows::~ListOfLows()
{
    delete ui;
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_low.clear();
    description_low.clear();
    formula_low.clear();
    select_group.clear();

}

void ListOfLows::on_pushButton_clicked()
{
    QString name = ui->name->text();
    QString description = ui->description->text();
    QString formula = ui->formula->text();
    if (name == "") {
        QMessageBox::critical(this, "Незаполненное поле", "Пожалуйста, заполните название закона!");
        return;
    }
    if ([=]() {
        foreach(Low *low, lowsgrouplist[ui->groups->currentText()]->list) {
            if (name == low->name) {
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
    lowsgrouplist[ui->groups->currentText()]->list << new Low(name, formula, description, params,
                                                        lowsgrouplist[ui->groups->currentText()]->color);
    QMessageBox::information(nullptr, "Добавление закона", "Закон успешно добавлен в систему!");
}

void ListOfLows::on_pushButton_2_clicked()
{
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_low.clear();
    description_low.clear();
    formula_low.clear();
    select_group.clear();
    this->close();
}

void ListOfLows::closeEvent(QCloseEvent *event)
{
    k1.clear();
    k2.clear();
    k3.clear();
    k4.clear();
    name_low.clear();
    description_low.clear();
    formula_low.clear();
    select_group.clear();
    QWidget::closeEvent(event);
    this->close();
}

void ListOfLows::on_formula_textChanged(const QString &arg1)
{
    ui->formulaView->setHtml("<html><head>" + scr + scroll_hide + "</head><body><p align='center'><font size='5'>$$" +
                             QString("{%1}$$").arg(arg1) + "</font></p></body></html>");
}
