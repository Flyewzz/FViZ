#include "fizitem.h"

FizItem& FizItem::operator =(const FizItem &another)
{
    name = another.name;
    symbol = another.symbol;
    this->level = another.level;
    L = another.L;
    T = another.T;
    G = another.G;
    k = another.k;
    x = another.x;
    y = another.y;
    unit_of_measurement = another.unit_of_measurement;
    symbol_unit_of_measurement = another.symbol_unit_of_measurement;
    return *this;
}

FizItem::FizItem(const qreal &x1, const qreal &y1, const int &l, const int &t,
                 const QColor &col) :x(x1), y(y1), L(l), T(t), level(col)
{
    name = "";
    visible = false;
    selected = false; //Изначально ячейка не выделена
    G = -101;
    k = -101;
    tex = nullptr;
}

FizItem::~FizItem()
{
    if (tex != nullptr) delete tex;
}

void FizItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget)
{
    if (!visible) return; //Элемент остается пустым, если информация о нем не заполнена
        painter->save();
        if (selected)
            painter->setPen(QPen(Qt::red, 2, Qt::DashLine));
        else
            painter->setPen(QPen(Qt::black, 1, Qt::SolidLine));
        const unsigned int n = 6;
        QPolygonF polygon;
        for (unsigned int i = 0; i < n; i++) {
            qreal fAngle = 2 * 3.14 * i / n;
            qreal x1 = x + sin(fAngle) * 65;
            qreal y1 = y - cos(fAngle) * 55;
            polygon << QPointF(x1, y1);
        }
        painter->setBrush(QBrush(level));
        painter->drawPolygon(polygon);
        painter->setFont(QFont("Times", 12, QFont::Normal));
        painter->restore();

}


void FizItem::setLevel(const int &a, const int &b)
{
    G = a;
    k = b;
}

void FizItem::RemoveCell()
{
    //Единственный ли это блок?
    bool find = [=]() {
         foreach (QString level, sysgroup.keys()) {
         FizItem *item = fizitems[level][T+N/2][T+L+N-6];
         if (item->name != "" && item_group[item->name] != item_group[name]) return true;
     }
         return false;
    }();
         /*Если отображаемый элемент единственный,
          * тогда очищаем клетку на поле
          */
    //Удаление на уровне

    // !Немного доработать!
    if (!find) {
    FizItem *it = fizitems[item_group[name]][T+N/2][T+L+N-6];
    item_group.remove(name);
    name = "";
    visible = false;
    if (getTex() != nullptr) getTex()->setVisible(false);
    update();
    it->name = "";
    it->visible = false;
    return;
    }
    foreach (QString level, sysgroup.keys()) {
    FizItem *item = fizitems[level][T+N/2][T+L+N-6];
    if (item->name != "" && item_group[item->name] != item_group[name]) {
        //! Ошибка!
      fizitems[item_group.value(name)][T+N/2][T+L+N-6]->name = "";
      item_group.remove(name);
      name = item->name;
      this->level = item->level;
      G = item->G;
      k = item->k;
      visible = true;
      update();
      getTex()->page()->setBackgroundColor(this->level);
      getTex()->setHtml(scr + scroll_hide + "<p align='left'><font size='1'>$$" + name + ",\\; " +
                            symbol +
                            QString("\\\\ {%1} $$").arg(value_c) +
                            "</font></p>");
      break;
    }
  }
}

QDataStream &operator << (QDataStream &stream, const FizItem &elem)
{
    stream << elem.name << elem.symbol << elem.unit_of_measurement
           << elem.symbol_unit_of_measurement << elem.value_c <<
              elem.L << elem.T << elem.G << elem.k
           << elem.level << elem.visible << elem.x << elem.y;
    //elem.x и elem.y ?
    return stream;
}

QDataStream &operator >>(QDataStream &stream, FizItem &elem)
{
    stream >> elem.name >> elem.symbol >> elem.unit_of_measurement
            >> elem.symbol_unit_of_measurement >> elem.value_c
            >> elem.L >> elem.T >> elem.G >> elem.k
           >> elem.level >> elem.visible >> elem.x >> elem.y;
    return stream;
}
void FizItem::ClearCell()
{
    visible = false;
    name = "";
}

void FizItem::setVisible(const bool &v)
{
    visible = v;
}

void FizItem::setSelect(const bool &flag)
{
    selected = flag;
    update();
}

bool FizItem::Select()
{
    selected = !selected;
    update();
    return selected;
}

void TextOut::setParent(FizItem *&p)
{
    parent = p;
}

FizItem *&TextOut::getParent()
{
    return parent;
}


