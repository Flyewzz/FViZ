#include "lowssettings.h"
#include "ui_lowssettings.h"

QHash<QString, LowsGroup*> lowsgrouplist; //Список всех групп законов
QColor ch_color; //Выбранный цвет для группы законов

//Изменение цвета группы законов
void changeLowsGroup(LowsGroup *&group, QColor &color) {
group->color = color;
foreach (Low *low, group->list) {
        low->color = color;
    }
}
LowsSettings::LowsSettings(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::LowsSettings)
{
    ui->setupUi(this);
    ui->color->setAutoFillBackground(true); // Обязательно
    QPalette palette;
    palette.setColor(QPalette::Background, Qt::black);
    ui->color->setPalette(palette);
    if (lowsgrouplist.empty()) {
        //Если нет ни одной группы законов, то блокируем кнопку удаления
        ui->remove_button->setEnabled(false);
        ui->add_button->clicked(); //Включаем режим создания нового закона
        return;
    }
    //Заполняем список названиями групп законов
    foreach(QString group_name, lowsgrouplist.keys()) {
        ui->comboBox->addItem(group_name);
        qDebug() << group_name; //Вывод списка групп законов для отладки
    }
    ui->comboBox->activated(ui->comboBox->currentText());
}

LowsSettings::~LowsSettings()
{
    delete ui;
}

void LowsSettings::on_toolButton_clicked()
{
    QMessageBox::information(nullptr, "", "Работает!");
}

void LowsSettings::on_pushButton_clicked()
{

    QString name = ui->group_name->text();
    if (name.length() == 0) {
        QMessageBox::warning(0, "Ошибка", "Поле названия не может быть пустым!");
        ui->group_name->setFocus();
        return;
    }
    if (ui->pushButton->text() == "Добавить") {
        //Проверка на дубликаты групп законов
        foreach (QString group_name, lowsgrouplist.keys())
            if (group_name == name) {
                QMessageBox::warning(0, "Дубликация групп законов", "Такая группа законов уже существует!");
                ui->group_name->clear();
                ui->group_name->setFocus();
                return;
        }
    ui->remove_button->setEnabled(true);
    lowsgrouplist[name] = new LowsGroup(ch_color);
    ui->group_name->clear();
    ui->group_name->setFocus();
    ui->comboBox->clear();
    //Выводим все группы законов
    foreach(QString group_name, lowsgrouplist.keys()) {
        ui->comboBox->addItem(group_name);
    }
    QMessageBox::information(nullptr, "Добавление группы законов", "Группа законов успешно добавлена!");
    }
    else if (ui->pushButton->text() == "Изменить") {
        QString old_name = ui->comboBox->currentText();
        if (old_name == name) {
            changeLowsGroup(lowsgrouplist[name], ch_color);
            goto m1; //См. ниже (переход без создания новой группы)
        }
      lowsgrouplist[name] = new LowsGroup(ch_color);
      foreach (Low *low, lowsgrouplist[old_name]->list) {
        lowsgrouplist[name]->list << low;
      }
      changeLowsGroup(lowsgrouplist[name], ch_color);
      lowsgrouplist[old_name]->list.clear();
      lowsgrouplist.remove(old_name);
      m1:
      ui->comboBox->clear();
      //Обновляем законы
      foreach(QString group_name, lowsgrouplist.keys()) {
          ui->comboBox->addItem(group_name);
      }
      QMessageBox::information(nullptr, "Редактирование группы законов", "Группа законов успешно обновлена!");
      ui->pushButton->setText("Добавить");
      ui->group_name->clear();
      ui->group_name->setFocus();
    }
}


void LowsSettings::on_color_button_clicked()
{
    //Установка цвета для группы законов
    QColor temp;
    temp = QColorDialog::getColor(temp, nullptr, tr("Цвет контура"));
    if (temp.isValid())
    {
        ch_color = temp;
        QPalette palette;
        palette.setColor(QPalette::Background, ch_color);
        ui->color->setPalette(palette);
    }
}

void LowsSettings::on_add_button_clicked()
{
    ui->pushButton->setText("Добавить");
    ui->group_name->clear();
    ui->group_name->update(); //Корректная перерисовка
    ui->group_name->setFocus();
}

void LowsSettings::on_comboBox_activated(const QString &arg1)
{
    ui->pushButton->setText("Изменить");
    ui->group_name->setText(arg1);
    QPalette palette;
    palette.setColor(QPalette::Background, lowsgrouplist[arg1]->color);
    ui->color->setPalette(palette);
}

QDataStream &operator <<(QDataStream &stream, const Low &low)
{
    stream << low.name << low.formula << low.description; //Сохраняем параметры закона
    for (int i = 0; i < 4; ++i) stream << low.e[i]; //Запись всех четырех величин
    stream << low.color; //Запись цвета закона
    return stream;
}

QDataStream &operator >>(QDataStream &stream, Low &low)
{
    stream >> low.name >> low.formula >> low.description; //Считываем параметры закона
    low.e.clear();
    QString var;
    for (int i = 0; i < 4; ++i) {stream >> var; low.e << var;} //Считывание всех четырех величин
    stream >> low.color; //Считывание цвета закона
    return stream;
}
