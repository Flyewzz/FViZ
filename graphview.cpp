//#include "graphview.h"
#include <QDebug>
#include "render_fizitem.h"

int L_click = 0;
int T_click = L_click;
QHash<QString, QVector<QVector<FizItem*>>> fizitems;
//Соответствие названия величины и названия ее системной группы
QHash<QString, QString> item_group;
bool change;
FizItem *ModScene::addFizItem(const int &x, const int &y,
                              const int &l, const int &t, const QColor &col)
{
    FizItem *item = new FizItem(x, y, l, t, col);
    this->addItem(item);
    //Возврат созданной ячейки
    return item;
}


FizItem* GraphView::create_element(const int &L, const int &T, const int &G, const int &k,
                               const QString &symbol, const QString &name, const QString &sys_c,
                               const QString &uom, const QString &suom, const QString &group,
                               const QColor &color)
{
    ///Доделать!
    if (main_view->out[T+N/2][T+L+N/2]->visible) {
        ///Работает!
       bool find = [=]() {\
            foreach (QString level, sysgroup.keys()) {
            FizItem *item = fizitems[level][T+N/2][T+L+N/2];
            if (group == item_group[item->name]) {
                return true;
            }
        }
            return false;
   }();
       if (!change_elem) {
            if (find){
                QMessageBox::warning(this, "Добавление элемента", "Элемент на данном уровне в этих координатах уже существует!");
            return nullptr;
            }
       }
            FizItem *item = fizitems[group][T+N/2][T+L+N/2];
            item->name = name;
            item->symbol = symbol;
            item->level = sysgroup[group]->color;
            item->value_c = sys_c;
            item->unit_of_measurement = uom;
            item->symbol_unit_of_measurement = suom;
            item_group[name] = group;
        return item;
    }

   //??? main_view->AddFizItem(L, T, G, k);
    FizItem *item = fizitems[group][T+N/2][T+L+N/2];
    item->name = name;
    item->symbol = symbol;
    item->level = sysgroup[group]->color;
    item->value_c = sys_c;
    item->unit_of_measurement = uom;
    item->symbol_unit_of_measurement = suom;
    item_group[name] = group;
    FizItem *it = main_view->out[T+N/2][T+L+N/2];
    it->visible = true;
    it->name = name;
    it->symbol = symbol;
    it->level = color;
    it->value_c = sys_c;
    it->unit_of_measurement = uom;
    it->symbol_unit_of_measurement = suom;
    it->setLevel(G, k);
    it->invalidatePixmap();
    it->update();

    return it;
}


void GraphView::remove_element(const QString &name, const int &L, const int &T)
{

    FizItem *item = out[T+N/2][T+L+N-6];
    item->RemoveCell();
}

FizItem* GraphView::AddFizItem(const int &L, const int &T)
{

    FizItem *item = scene.addFizItem(gX, gY, L, T, Qt::cyan);
   // out[L+N/2][T+N/2] = scene.addFizItem(gX, gY, L, T, Qt::cyan);
    return item;
}

void GraphView::ClearField()
{
    for (int i = 0; i < N; ++i)
        foreach (FizItem *it, out[i]) {
            it->name = "";
            it->invalidatePixmap();
            it->update();
            it->visible = false;
        }
}

void GraphView::AllUpdate()
{
    for (int i = 0; i < N; ++i)
        foreach (FizItem *it, out[i]) {
            if (it->name == "") continue;
            it->invalidatePixmap();
            it->update();
        }
}

GraphView::~GraphView()
{
}

void GraphView::contextMenuEvent(QContextMenuEvent *event)
{
    select = dynamic_cast<FizItem*>(itemAt(event->pos()));

    if (!select) {
       //Отлавливаем нажатия на текстовые поля для вывода информации блока
       QGraphicsProxyWidget *to = dynamic_cast<QGraphicsProxyWidget*>(itemAt(event->pos()));
       if (!to) return;
       select = text_assoc[to];
    }
    if (!select || !select->visible) {
    menu->exec(event->globalPos());
    return;
    }
    L_click = select->L;
    T_click = select->T;
    //Очистка прошлого меню выбора уровней
    if (level_menu != nullptr) {
        disconnect(level_menu, SIGNAL(triggered(QAction*)), this, SLOT(select_level(QAction*)));
        foreach (QAction *act, level_menu->actions()) {
            level_menu->removeAction(act);
            delete act;
        }
        delete level_menu;
        level_menu = nullptr;
    }
    //Очистка прошлого меню (общего)
    if (menu_element != nullptr) {
        disconnect(menu_element, SIGNAL(triggered(QAction*)), this, SLOT(slotActivated(QAction*)));
        foreach (QAction *act, menu_element->actions()) {
            menu_element->removeAction(act);
            delete act;
        }
        delete menu_element;
        menu_element = nullptr;
    }
    //Создаем и связываем новые меню
    menu_element = new QMenu(this);
    level_menu = new QMenu;
    level_menu->setTitle("Уровни");
    /// :))) item_group.clear();
    //Здесь нам нужно наполнить список для выбора других элементов
    bool add = false;
    foreach (QString level, sysgroup.keys()) {
        QString item = fizitems[level][select->T+N/2][select->T+select->L+N/2]->name;
        if (item_group[select->name] != level && item != "") {
            level_menu->addAction(item);
            add = true;
        }
    }
    menu_element->addAction("Редактировать");
    menu_element->addAction(QIcon(":/pics/pics/delete.png"), "Удалить");
    //Коннект меню
    connect(menu_element, SIGNAL(triggered(QAction*)), SLOT(slotActivated(QAction*)));
    connect(level_menu, SIGNAL(triggered(QAction*)), SLOT(select_level(QAction*)));
    /* Добавляем пункт "Уровни"
        только если элементов в данных LT координатах больше одного */
    if (add) menu_element->addMenu(level_menu);
    menu_element->exec(event->globalPos());
}

void GraphView::mousePressEvent(QMouseEvent *event)
{
    if (event->button() != Qt::LeftButton) return;
    select = dynamic_cast<FizItem*>(itemAt(event->pos())); //Получение выделенного элемента
            if (!select) {
                //Если получено текстовое поле на самом элементе, возвращаем сам элемент
            QGraphicsProxyWidget *to = dynamic_cast<QGraphicsProxyWidget*>(itemAt(event->pos()));
            if (!to) {
                /*Если не выделено ничего, тогда очищаем нарисованный polygon,
                 * затем отменяем предыдущее выделение */
                polygon.clear();
                if (ittt == nullptr) return;
                delete ittt;
                ittt = nullptr;
                foreach (FizItem *item, selected_items)
                    item->setSelect(false);
                selected_items.clear();
                return;
            }
            select = text_assoc[to];
            }
            if (!select->visible) return;
            if (select->Select())
                selected_items << select;
            else {
                selected_items.removeOne(select);
                if (ittt != nullptr) {polygon.clear(); delete ittt; ittt = nullptr;}
            }
            size_t select_size = selected_items.size();
            if (select_size == 3 || select_size == 4) {
//                for (int i = 0; i < selected_items.length(); ++i)
//                    qDebug() << "L^" <<selected_items[i]->L << "T^" << selected_items[i]->T;
                qSort(selected_items.begin(), selected_items.end(),
                      [](const FizItem *a, const FizItem *b) {
                    if (a->L == b->L) return (a->T > b->T);
                    return a->L > b->L;
                });
            FizItem *&e1 = selected_items[0]; //Находим левый верхний элемент
//                qDebug() << "1:";
                qSort(selected_items.begin()+1, selected_items.end(),
                      [](const FizItem *a, const FizItem *b) {
                    if (a->L == b->L) return a->T < b->T;
                    return a->L < b->L;
                });
                FizItem *&e2 = selected_items[1]; //Находим правый нижний элемент
//                for (int i = 0; i < selected_items.length(); ++i)
//                    qDebug() << "L^" <<selected_items[i]->L << "T^" << selected_items[i]->T;
                FizItem *&e3 = selected_items[2];
                FizItem *e4 = e3; //Криво, но работает
                if (select_size == 4) e4 = selected_items[3];

                bool check_G = (e1->G + e2->G == e3->G + e4->G);
                bool check_k = (e1->k + e2->k == e3->k + e4->k);
                bool check_L = (e1->L + e2->L == e3->L + e4->L);
                bool check_T = (e1->T + e2->T == e3->T + e4->T);
                //########
                //Проверка соотношений для построения параллелограмма
                bool check = check_G && check_k && check_L && check_T;
                if (!check) return;
                FizItem *temp = e2;
                e2 = e3;
                e3 = temp;
                // Строим параллелограмм правильно (!)
                for (int i = 0; i < selected_items.length(); ++i)
                    polygon << QPointF(selected_items[i]->x, selected_items[i]->y);
                QPen pen;
                Low *find_low = [=]() {
                    QVector<QString> vec;
                    vec << e1->getName() << e3->getName() << e2->getName() << e4->getName();
                    foreach (QString group, lowsgrouplist.keys()) {
                        foreach (Low *low, lowsgrouplist[group]->list) {
                            if (vec == low->e) {
                                select_group = group;
                                vec.clear();
                                return low;
                            }
                        }
                    }
                    vec.clear();
                    return static_cast<Low*>(nullptr);
                }();
               if (find_low == nullptr) pen.setColor(Qt::black);
               else {
                   pen.setColor(find_low->color);
                   name_low = find_low->name;
                   description_low = find_low->description;
                   formula_low = find_low->formula;
               }
                pen.setWidth(4);
             ittt = scene.addPolygon(polygon, pen);
             //Передача названий величин форме для добавления/изменения законов
             k1 = e1->getName(); k2 = e3->getName(); k3 = e2->getName(); k4 = e4->getName();
             QTimer *timer = new QTimer;
             timer->setInterval(800);
             timer->start();
             connect(timer, &QTimer::timeout, [timer](){
             ListOfLows *w = new ListOfLows;
             w->show();
             timer->stop();
             delete timer;
            });
       }
}

void GraphView::mouseMoveEvent(QMouseEvent *event)
{
    FizItem *item = dynamic_cast<FizItem*>(itemAt(event->pos()));
    //Игнорируем пустую область
    if (!item) {
        //Отлавливаем нажатия на текстовые поля для вывода информации блока
        QGraphicsProxyWidget *to = dynamic_cast<QGraphicsProxyWidget*>(itemAt(event->pos()));
        if (!to) return;
       //item = to->getParent();
        item = text_assoc[to];
    };
    position->setText(QString("L<sup>%1</sup>T<sup>%2</sup>").arg(item->L).arg(item->T));
    if (item->visible) {
    Gk->setText(QString("G<sup>%1</sup>k<sup>%2</sup>").arg(item->G).arg(item->k));
    name_izm->setText(item->unit_of_measurement + ", " + item->symbol_unit_of_measurement);
    }
    else {
      Gk->setText("Gk");
      name_izm->setText("ед.изм");
    }
}

void GraphView::mouseDoubleClickEvent(QMouseEvent *event)
{
  FizItem *item = dynamic_cast<FizItem*>(itemAt(event->pos()));
  if (!item) {
      //Отлавливаем нажатия на текстовые поля для вывода информации блока
      QGraphicsProxyWidget *to = dynamic_cast<QGraphicsProxyWidget*>(itemAt(event->pos()));
      if (!to) return;
      //item = to->getParent();
      item = text_assoc[to];
  }

  L_click = item->L;
  T_click = item->T;
  change_elem = false;
  //Очищаем выделение элементов на сцене
  foreach (FizItem *item, selected_items)
      item->setSelect(false);
  selected_items.clear();
  //Вызываем форму для добавления/редактирования элементов
  AddElement *form = new AddElement;
  form->show();
}

void GraphView::wheelEvent(QWheelEvent *event)
{

    //Константа изменения масштаба главной сцены
    const double scaleFactor = 1.08;
    //Zoom in
    if (event->delta() > 0) {
        scale(scaleFactor, scaleFactor);
        QGraphicsView::wheelEvent(event);
        return;
    }
    //Zoom out
    scale(1.0/scaleFactor, 1.0/scaleFactor);
    QGraphicsView::wheelEvent(event);
}

void GraphView::slotActivated(QAction *act)
{
  QString choose = act->text().remove("&");
  if (choose == "Добавить") {

      change_elem = false;
      AddElement *form = new AddElement;
      QPoint point = main_window->mapToGlobal(QPoint(main_view->pos().x() - 300,
                                              main_view->pos().y() + 50));
      form->move(point);
      form->show();
    //  form->set(main_window.x() - 100, main_view->pos().y());
  }
  //!!! select->name != ""
  else if (choose == "Удалить" && select->name != "") {
      ///Рассмотрим выбор меню удаления

     undo << new Command_Element(select->L, select->T, select->G, select->k,
                                 select->symbol, select->name, select->value_c,
                                 select->unit_of_measurement, select->symbol_unit_of_measurement,
                                 item_group[select->name], select->level, 1);
     undo_action->setEnabled(true);
     foreach (Command *command, redo) {
         delete command;
     }
     redo.clear();
     redo_action->setEnabled(false);
     select->RemoveCell();
  }
  else if (choose == "Редактировать" && select->name != "") {
//     if (item->name == "") //Если кликнули в пустую область, то добавляем новый элемент
//         change_elem = false;
//     else
         change_elem = true; // Изменение элемента при клике
         //Очищаем выделение элементов на сцене
         foreach (FizItem *item, selected_items) {
             item->setSelect(false);
         }
         selected_items.clear();
         AddElement *form = new AddElement;
         QPoint point = main_window->mapToGlobal(QPoint(main_view->pos().x() - 300,
                                                 main_view->pos().y() + 50));
         form->move(point);
         form->show();
     }
}

void GraphView::select_level(QAction *act)
{
   QString choose = act->text();

   FizItem *item = fizitems[item_group.value(choose)][select->T+N/2][select->T+select->L+N/2];
   select->assign(*item);
   select->update();
}

void InitializeField::fill_line()
{
    QVector<FizItem*> line;
    for (int j = 0; j < N; ++j) {
        FizItem *it = main_view->AddFizItem(j-line_number, line_number-N/2);
        line << it;
        it->setVisible(true); // (для отладки)
        //it->setFlags(QGraphicsItem::ItemIsSelectable);;
        gX += 59;
        gY -= 88;

    }
     //Блокируем вывод на форму, пока не добавили созданные элементы в текущем потоке
    main_view->out << line;
    line.clear();
    gX -= 59 * N;
    gY += 88 * N;
    /*
    gX -= 59;
    gY -= 88;
    */
    gX -= 119;
    emit finished(); //Работа завершена
}
