#include "lawssettings.h"
#include "ui_lawssettings.h"

QHash<QString, LawsGroup*> lawsgrouplist; //Список всех групп законов
QColor ch_color; //Выбранный цвет для группы законов

//Изменение цвета группы законов
void changeLawsGroup(LawsGroup *&group, QColor &color) {
group->color = color;
foreach (Law *law, group->list) {
        law->color = color;
    }
}
LawsSettings::LawsSettings(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::LawsSettings)
{
    ui->setupUi(this);
    ui->color->setAutoFillBackground(true); // Обязательно
    QPalette palette;
    palette.setColor(QPalette::Background, Qt::black);
    ui->color->setPalette(palette);
    if (lawsgrouplist.empty()) {
        //Если нет ни одной группы законов, то блокируем кнопку удаления
        ui->remove_button->setEnabled(false);
        ui->add_button->clicked(); //Включаем режим создания нового закона
        return;
    }
    //Заполняем список названиями групп законов
    foreach(QString group_name, lawsgrouplist.keys()) {
        ui->comboBox->addItem(group_name);
        qDebug() << group_name; //Вывод списка групп законов для отладки
    }
    ui->comboBox->activated(ui->comboBox->currentText());
}

LawsSettings::~LawsSettings()
{
    delete ui;
}

void LawsSettings::on_toolButton_clicked()
{
    QMessageBox::information(this, "", "Работает!");
}

void LawsSettings::on_pushButton_clicked()
{

    QString name = ui->group_name->text();
    if (name.length() == 0) {
        QMessageBox::warning(this, "Ошибка", "Поле названия не может быть пустым!");
        ui->group_name->setFocus();
        return;
    }
    if (ui->pushButton->text() == "Добавить") {
        //Проверка на дубликаты групп законов
        foreach (QString group_name, lawsgrouplist.keys())
            if (group_name == name) {
                QMessageBox::warning(this, "Дубликация групп законов", "Такая группа законов уже существует!");
                ui->group_name->clear();
                ui->group_name->setFocus();
                return;
        }
    ui->remove_button->setEnabled(true);
    lawsgrouplist[name] = new LawsGroup(ch_color);
    ui->group_name->clear();
    ui->group_name->setFocus();
    ui->comboBox->clear();
    //Выводим все группы законов
    foreach(QString group_name, lawsgrouplist.keys()) {
        ui->comboBox->addItem(group_name);
    }
    QMessageBox::information(this, "Добавление группы законов", "Группа законов успешно добавлена!");
    }
    else if (ui->pushButton->text() == "Изменить") {
        QString old_name = ui->comboBox->currentText();
        if (old_name == name) {
            changeLawsGroup(lawsgrouplist[name], ch_color);
            goto m1; //См. ниже (переход без создания новой группы)
        }
      lawsgrouplist[name] = new LawsGroup(ch_color);
      foreach (Law *law, lawsgrouplist[old_name]->list) {
        lawsgrouplist[name]->list << law;
      }
      changeLawsGroup(lawsgrouplist[name], ch_color);
      lawsgrouplist[old_name]->list.clear();
      lawsgrouplist.remove(old_name);
      m1:
      ui->comboBox->clear();
      //Обновляем законы
      foreach(QString group_name, lawsgrouplist.keys()) {
          ui->comboBox->addItem(group_name);
      }
      QMessageBox::information(this, "Редактирование группы законов", "Группа законов успешно обновлена!");
      ui->pushButton->setText("Добавить");
      ui->group_name->clear();
      ui->group_name->setFocus();
    }
}


void LawsSettings::on_color_button_clicked()
{
    //Установка цвета для группы законов
    QColor temp;
    temp = QColorDialog::getColor(temp, this, tr("Цвет контура"));
    if (temp.isValid())
    {
        ch_color = temp;
        QPalette palette;
        palette.setColor(QPalette::Background, ch_color);
        ui->color->setPalette(palette);
    }
}

void LawsSettings::on_add_button_clicked()
{
    ui->pushButton->setText("Добавить");
    ui->group_name->clear();
    ui->group_name->update(); //Корректная перерисовка
    ui->group_name->setFocus();
}

void LawsSettings::on_comboBox_activated(const QString &arg1)
{
    ui->pushButton->setText("Изменить");
    ui->group_name->setText(arg1);
    QPalette palette;
    palette.setColor(QPalette::Background, lawsgrouplist[arg1]->color);
    ui->color->setPalette(palette);
}

QDataStream &operator <<(QDataStream &stream, const Law &law)
{
    stream << law.name << law.formula << law.description; //Сохраняем параметры закона
    for (int i = 0; i < 4; ++i) stream << law.e[i]; //Запись всех четырех величин
    stream << law.color; //Запись цвета закона
    return stream;
}

QDataStream &operator >>(QDataStream &stream, Law &law)
{
    stream >> law.name >> law.formula >> law.description; //Считываем параметры закона
    law.e.clear();
    QString var;
    for (int i = 0; i < 4; ++i) {stream >> var; law.e << var;} //Считывание всех четырех величин
    stream >> law.color; //Считывание цвета закона
    return stream;
}
