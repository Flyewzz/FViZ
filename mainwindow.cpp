#include "mainwindow.h"
#include "ui_mainwindow.h"

QHash<QGraphicsProxyWidget*, FizItem*> text_assoc;
int choose;
int N = 12; //Размеры рабочей области (LT)
//Хэш параметров системных групп ФВ
QHash<QString, SysGroup*> sysgroup;
QDir dir = QDir::current();
QString scr;
QString scroll_hide = "<style type='text/css'>"
       " body {"
        "    overflow:hidden;"
       " }"
       "</style>";
double gX, gY;
GraphView *main_view;
QLabel *position;
QLabel *Gk;
QLabel *name_izm;
//Файл для взаимодействия с базой данных элементов
QFile work_file;
//Файловый поток ввода-вывода
QDataStream work_stream;
//Путь до рабочего файла
QString work_str;
QAction *undo_action;
QAction *redo_action;

QMainWindow *main_window;

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{

//   scr = "<script "
//           "src='MathJax/unpacked/MathJax.js?config=TeX-AMS-MML_HTMLorMML'>"
//         "</script>";
    scr = "<script "
               "src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-AMS-MML_HTMLorMML'>"
             "</script>";
   /*
    scr = "<script "
            "src='" + st + "?config=TeX-AMS-MML_HTMLorMML'>"
          "</script>";
          */
  // qDebug() << scr;
//    qDebug() << dir.path();
    ui->setupUi(this);
    main_window = this;
    main_view = ui->graphicsView;
    CreateActions();
    undo_action = ui->action_13;
    redo_action = ui->action_19;
    //Доработать
    undo_action->setEnabled(false);
    redo_action->setEnabled(false);
    position = ui->position;
    Gk = ui->Gk;
    name_izm = ui->name_izm;
    work_stream.setDevice(&work_file); //Синхронизация файлового потока и рабочего файла
    ui->action_2->setShortcut(QKeySequence("Alt+O"));
    //###### Настройка пунктов меню ###############################################################
    //Настройка меню "Открыть"
    ui->action_6->setIcon(QIcon(QApplication::style()->standardIcon(QStyle::SP_DialogOpenButton)));
    //Настройка меню "Сохранить"
    ui->action_9->setIcon(QIcon(QApplication::style()->standardIcon(QStyle::SP_DialogSaveButton)));
    //#############################################################################################
    gX = main_view->width()/2.0 + 1400;
    gY = main_view->height()/2.0 + 1300;
    //Доделать расчет центрирования L^0T^0
    main_view->horizontalScrollBar()->setSliderPosition(main_view->width()/2.0 + 1000.0);
    main_view->verticalScrollBar()->setSliderPosition(main_view->height()/2.0 + 800.0);
    change = false;
    /*
    CreateSysGroup("Кинематические величины", 0, 0, Qt::red);
    CreateSysGroup("Общие базовые величины", 1, 2, Qt::yellow);
    CreateSysGroup("Электромеханические величины", -1, 0, Qt::darkCyan);
    */
    main_view->setInteractive(true);
        for (int i = 0; i < N; ++i) {
            QVector<FizItem*> line;
            for (int j = 0; j < N; ++j) {
                FizItem *it = main_view->AddFizItem(j-N/2-i+6, i-N/2);
                line << it;
//                it->setVisible(true); // (для отладки)
                //it->setFlags(QGraphicsItem::ItemIsSelectable);
                it->getTex() = new TextOut;
                it->getTex()->setParent(it);
                it->getTex()->setVisible(false);
                it->getTex()->setGeometry(gX - 55, gY - 27, 110, 54);
                it->getTex()->setHtml(scroll_hide); //Выключаем скроллы
              //  it->getTex()->settings()->setAttribute(Qt::TextWordWrap, true);
              // mutex.lock();
               text_assoc.insert(main_view->scene.addWidget(it->getTex()), it);
                gX += 59;
                gY -= 88;
               // mutex.unlock();
            }
           // mutex.lock(); //Блокируем вывод на форму, пока не добавили созданные элементы в текущем потоке
            main_view->out << line;
            line.clear();
            gX -= 59 * N;
            gY += 88 * N;
            /*
            gX -= 59;
            gY -= 88;
            */
            gX -= 119;
           // mutex.unlock();
            /*
          QThread *thread = new QThread;
          InitializeField init(i);
          connect(thread, SIGNAL(started()), &init, SLOT(fill_line()));
          connect(&init, SIGNAL(finish()), thread, SLOT(terminate()));
          init.moveToThread(thread);
          thread->start();
          */
        }
        /*
        //  ################(для отладки) ##################################
        work_str = "/Users/igor/Desktop/Программа Чуев/Супер.fviz";
        work_file.setFileName(work_str);
        // На случай, если тестовый файл будет перемещен
        if (!work_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QMessageBox::critical(nullptr, "Ошибка", "Файл не может быть открыт!");
            return;
        }
        Open();
        // ##################################################################
        General_Settings *w = new General_Settings;
        w->move(this->width() + 1, 0);
        w->show();
        w->update();
        QPropertyAnimation *animation = new QPropertyAnimation(w, "pos", this);
        animation->setDuration(1000);
        animation->setStartValue(this->pos());
        animation->setEndValue(QPoint(0, 0));
        animation->start();
        */
}

void MainWindow::ClearStruct() {
    //Процедура полной очистки памяти программы
    //???

    //Очистка видимого поля
    for (int i = 0; i < main_view->out.length(); ++i) {
    foreach (FizItem *wb, main_view->out[i]) {
        delete wb;
    }
    main_view->out[i].clear();
  }
    //Итоговая очистка поля
    main_view->out.clear();
    //foreach (main, container) {

   // }
    foreach (QString name, sysgroup.keys())
        RemoveSysGroup(name);
    sysgroup.clear();
    item_group.clear();
    //Полная очистка всей многоуровневой системы FViZ
    foreach (QString level, fizitems.keys()) {
        for (int i = 0; i < fizitems[level].size(); ++i) {
            foreach (FizItem *item, fizitems[level][i]) {
                //Очищаем каждую ячейку в строке
                delete item;
            }
        fizitems[level][i].clear(); //Очищаем каждую строку
        }
        fizitems[level].clear(); //Очистка целого уровня
        fizitems.remove(level);
    }
    fizitems.clear(); //Финальная очистка структуры
    foreach (QString group, lowsgrouplist.keys()) { //Перебираем все группы законов
        foreach (Low *low, lowsgrouplist[group]->list) {
            low->e.clear(); //Очищаем названия величин для каждого закона
            delete low; //Удаляем текущий закон
        }
        delete lowsgrouplist[group]; //Удаляем текущую группу законов
    }
    lowsgrouplist.clear(); //Финальная очистка структуры для хранения группы законов
}

void MainWindow::Save()
{
    /*
    work_stream << N; //Запомним размеры сцены (в LT координатах)
    qDebug() << "Размер сцены: " << N;
    */
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
           work_stream << *main_view->out[i][j];
        ///Осторожно! Не забыть, что настоящее N должно быть больше
       // stream << N;
        //Запоминаем количество уровней
        int count_of_levels = sysgroup.size();
        ///(!)
        work_stream << count_of_levels;
        //Запоминаем уровни
        foreach (QString key, sysgroup.keys()) {
            ///Важно передавать саму структуру, а не указатель на нее (!!!)
          work_stream << key << *sysgroup[key];
        }
        //и их содержимое...
        foreach (QString level, fizitems.keys()) {
            for (int i = 0; i < N; ++i)
                for (int j = 0; j < N; ++j)
                    work_stream << level << *fizitems[level][i][j];
        }
        int count_of_itemgroups = item_group.size();
        // qDebug() << "Количество itemgroup: " << count_of_itemgroups;
        //Запоминаем соответствие названия имен блоков и их уровней
        work_stream << count_of_itemgroups;
        foreach (QString cell_name, item_group.keys()) {
            work_stream << cell_name << item_group[cell_name];
        }
        //Запоминаем количество групп законов и их характеристики
        int count_of_lowsgroups = lowsgrouplist.size();
        //qDebug() << "Количество групп законов: " << count_of_lowsgroups;
        work_stream << count_of_lowsgroups;
        foreach (QString group_name, lowsgrouplist.keys()) {
            work_stream << group_name; //Записываем имя группы закона
            work_stream << lowsgrouplist[group_name]->color; //Записываем ее цвет
            //Записываем количество законов данной группы
            int lows_count = lowsgrouplist[group_name]->list.length();
            work_stream << lows_count;
            foreach (Low *low, lowsgrouplist[group_name]->list) {
               work_stream << *low; //Записываем текущий закон (см. перегрузки lowssettings.h и .cpp)
            }
        }
        work_file.close();
}

void MainWindow::Open()
{
    /*
    unsigned int check_number;
    work_stream >> check_number; //Проверка размеров сцены (в LT координатах)

    qDebug() << "N = " << check_number;
    if (check_number != N) {
        work_file.close();
        QMessageBox::critical(nullptr, "Несоответствие размеров", "Размер сцены в файле"
                                                            " отличается от требуемого!");
        return;
    }
    */
    main_view->setCursor(Qt::WaitCursor);
    main_view->ClearField(); //Общая очистка видимого поля
//    Сделать очистку сцены
    foreach (QString var, sysgroup.keys()) {
        RemoveSysGroup(var);
    }
    sysgroup.clear();
    item_group.clear();
    foreach (QString group_name, lowsgrouplist.keys()) {

        foreach (Low *low, lowsgrouplist[group_name]->list) {
            delete low;
        }
        lowsgrouplist[group_name]->list.clear();
        lowsgrouplist.remove(group_name);
    }
    lowsgrouplist.clear(); //Очистка старого списка групп законов

    ///Осторожно! Не забыть, что настоящее N должно быть больше
        //qDebug() << "Этап инициализации поля";
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j) {
                work_stream >> *main_view->out[i][j];
               // qDebug() << main_view->out[i][j]->getName();
            }
    int count_of_levels;
    ///(!)
    work_stream >> count_of_levels;
    //Вспоминаем уровни
   // qDebug() << "Этап системных групп";
    for (int i = 0; i < count_of_levels; ++i) {
      QString key;
      SysGroup *group = new SysGroup(0, 0, Qt::black);
      work_stream >> key >> *group;
      CreateSysGroup(key, group->G, group->k, group->color);
      delete group;
     // qDebug() << key << " ";
    }
    //и их содержимое...
   // qDebug() << "Этап заполнения уровней";
    for (int t = 0; t < count_of_levels; ++t)
        for (int i = 0; i < N; ++i)
            for (int j = 0; j < N; ++j) {
                QString level;
                work_stream >> level;
                work_stream >> *fizitems[level][i][j];
               // qDebug() << level << fizitems[level][i][j]->getName() << " ";
            }
    int count_of_itemgroups;
    //Вспоминаем соответствие названия имен блоков и их уровней
   // qDebug() << "Этап заполнения соответствий блоков и имен их СГ";
    work_stream >> count_of_itemgroups;
    for (int i = 0; i < count_of_itemgroups; ++i) {
        QString cell_name;
        QString value;
        work_stream >> cell_name >> value;
        item_group[cell_name] = value;
      //  qDebug() << "Имя: " << cell_name << " Системная группа: " << item_group[cell_name];
    }
    //Количество групп законов и их характеристики
    int count_of_lowsgroups;
    work_stream >> count_of_lowsgroups;
    //qDebug() << "Количество групп законов: " << count_of_lowsgroups;
    for (int i = 0; i < count_of_lowsgroups; ++i) {
        QString group_name;
        work_stream >> group_name; //Имя группы закона
        QColor color;
        work_stream >> color; //Записываем ее цвет
        //Количество законов данной группы
        int lows_count;
        work_stream >> lows_count;
       // qDebug() << "Количество законов:" << lows_count;
        QList<Low*> list;
        for (int j = 0; j < lows_count; ++j) {
           Low *low = new Low;
           work_stream >> *low; //Записываем текущий закон (см. перегрузки lowssettings.h и .cpp)
           list << low;
        }
       lowsgrouplist[group_name] = new LowsGroup(color, list);
    }
    work_file.close();
    main_view->AllUpdate();
    main_view->setCursor(Qt::ArrowCursor);
}

void MainWindow::CreateActions()
{
    QToolBar *main_toolbar = addToolBar("Main_ToolBar");
    //Добавление основных команд (Открытие и Сохранение)
    main_toolbar->addAction(ui->action_6);
    main_toolbar->addAction(ui->action_9);
    main_toolbar->addSeparator();
    //Добавление команды "Экспорт таблицы"
    main_toolbar->addAction(ui->action_12);
    main_toolbar->addSeparator();
    //Добавление команд "Отменить" и "Повторить"
    main_toolbar->addAction(ui->action_13);
    main_toolbar->addAction(ui->action_19);
}

MainWindow::~MainWindow() //Главный деструктор программы
{
    ClearStruct(); //Процедура полной очистки памяти программы
    delete ui;
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    ClearStruct();
    QMainWindow::closeEvent(event);
}
void MainWindow::on_action_2_triggered()
{
    About *ab = new About;
    ab->show();
}

void MainWindow::on_action_3_triggered()
{
   AddSysGroup *w = new AddSysGroup;
   w->show();
}

void CreateSysGroup(const QString &name, const int &G, const int &k, const QColor &col)
{
   sysgroup[name] = new SysGroup(G, k, col);
   QVector<QVector<FizItem*>> field;
       QVector<FizItem*> line;
           for (int i = 0; i < N; ++i) {
               for (int j = 0; j < N; ++j) {
                   FizItem *elem = new FizItem(0, 0, j-N/2, i-N/2);
                   elem->setLevel(G, k);
                   line << elem;
               }
               field << line;
               line.clear();
       }
    fizitems[name] = field;
}

void RemoveSysGroup(const QString &name)
{
    /* ?
    if (!sysgroup.contains(name)) return;
    for (int i = 0; i < fizitems[name].size(); ++i)
        fizitems[name][i].clear();
    */
    for (int i = 0; i < fizitems[name].size(); ++i) {
        foreach (FizItem *item, fizitems[name][i]) {
            //Очищаем каждую ячейку в строке
            delete item;
        }
    fizitems[name][i].clear(); //Очищаем каждую строку
    }
    fizitems[name].clear(); //Очистка целого уровня
    fizitems.remove(name);
    sysgroup.remove(name);
}

QDataStream &operator <<(QDataStream &stream, const SysGroup &elem)
{
    stream << elem.G << elem.k << elem.color;
    return stream;
}

QDataStream &operator >>(QDataStream &stream, SysGroup &elem)
{
    stream >> elem.G >> elem.k >> elem.color;
    return stream;
}

void MainWindow::on_action_6_triggered()
{
    QString temp = work_str;
    work_str = QFileDialog::getOpenFileName(this, "Открытие сцены", "/", "*fviz");
    if (work_str.isEmpty()) {
        work_str = temp;
        return; //При отмене вернуться
    }
    work_file.setFileName(work_str);
    if (!work_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QMessageBox::critical(nullptr, "Ошибка", "Файл не может быть открыт!");
        return;
    }
    Open();
}

void MainWindow::on_action_10_triggered()
{

    QString temp = work_str;
    work_str = QFileDialog::getSaveFileName(this, "Сохранение сцены", "/", "*.fviz");
    if (work_str.isEmpty()) {
        work_str = temp;
        return;
    }
    work_file.setFileName(work_str);
    if (!work_file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QMessageBox::critical(nullptr, "Ошибка", "Ошибка сохранения сцены!");
        return;
    }
    Save();
    QMessageBox::information(nullptr, "Сохранение сцены", "Сцена успешно загружена в файл!");
}


void MainWindow::on_action_9_triggered()
{
   if (!work_file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QMessageBox::critical(nullptr, "Ошибка", "Ошибка сохранения сцены!");
        return;
   }
   Save();
}

void MainWindow::on_action_12_triggered()
{
    //Сохранение изображения сцены
    QString str = QFileDialog::getSaveFileName(nullptr, QCoreApplication::applicationDirPath(),
                                               "*.png" );
   if (str.isEmpty()) return;
   QPixmap pixmap = main_view->grab();
   pixmap.save(str);
}

void MainWindow::on_action_5_triggered()
{
    LowsSettings *w = new LowsSettings;
    w->show();
}

void MainWindow::on_action_11_triggered()
{
    //!!! ПЕРЕДЕЛАТЬ НАЗВАНИЕ listoflows !!!
    ListOfLows *y = new ListOfLows;
    y->show();
}

void MainWindow::on_action_8_triggered()
{
    MainList *w = new MainList;
    w->show();
}

void MainWindow::on_MainWindow_destroyed()
{
    ClearStruct();
    this->close();
}

void MainWindow::on_action_7_triggered()
{
    ClearStruct();
    this->close();
}


void MainWindow::on_action_13_triggered()
{
    undo.pop()->execute();
    if (undo.empty()) undo_action->setEnabled(false);
}

void MainWindow::on_action_19_triggered()
{
    redo.pop()->execute();
    if (redo.empty()) redo_action->setEnabled(false);
}

void MainWindow::on_action_14_triggered()
{
    General_Settings *w = new General_Settings;
    w->show();
}

void MainWindow::on_action_16_triggered()
{
}

void EditSysGroup(QString old_name, QString new_name, const int &G, const int &k, const QColor &col)
{
    SysGroup *old_sysgroup = sysgroup[old_name];
    old_sysgroup->G = G;
    old_sysgroup->k = k;
    old_sysgroup->color = col;
    sysgroup[new_name] = old_sysgroup;
    sysgroup.remove(old_name);

    QVector<QVector<FizItem*>> &field = fizitems[old_name];
    fizitems[new_name] = field;
    for (QVector<FizItem*> line : field) {
        for (FizItem *item : line) {
          item_group[item->getName()] = new_name;
        }
    }
    fizitems.remove(old_name);
}
