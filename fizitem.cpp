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

    unit_of_measurement = another.unit_of_measurement;
    symbol_unit_of_measurement = another.symbol_unit_of_measurement;
    pixmapOutdated = another.pixmapOutdated;
    if (!pixmapOutdated) {
        cachedPixmap = another.cachedPixmap;
    }
    return *this;
}

FizItem::FizItem(const int l, const int t,
                 const QColor &col) : L(l), T(t), level(col)
{
    name = "";
    visible = false;
    selected = false; //Изначально ячейка не выделена
    G = -101;
    k = -101;
}

FizItem::~FizItem()
{
}

void FizItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget)
{
    if (!visible) return; //Элемент остается пустым, если информация о нем не заполнена

    painter->save();

    if (selected)
        painter->setPen(QPen(Qt::red, 2, Qt::DashLine));
    else
        painter->setPen(QPen(Qt::black, 1, Qt::SolidLine));

    painter->setBrush(QBrush(level));
    painter->drawPolygon(boundingPolygon());

    if (name != "") {
        if (pixmapOutdated) {
            if (renderRequest == 0) {
                renderRequest = renderer->Render(this, QSize(kTextSizeX, kTextSizeY), kTextScale, [=](const QPixmap &pixmap) {
                    setPixmap(pixmap);
                    renderRequest = 0;
                    update();
                });
            }
        } else {
            painter->drawPixmap(xPos() - kTextSizeX/2, yPos() - kTextSizeY/2, cachedPixmap);
        }
    }

    painter->restore();
}

void FizItem::invalidatePixmap() {
    if (renderRequest != 0) {
        renderer->Cancel(renderRequest);
        renderRequest = 0;
    }
    pixmapOutdated = true;
}

QPolygon FizItem::boundingPolygon() const {
    QPolygon polygon;
    const int x = xPos();
    const int y = yPos();

    for (int i = 0; i != kPolygonN; ++i) {
        qreal fAngle = 2 * 3.14 * i / kPolygonN;
        int x1 = int(x + sin(fAngle) * kItemSizeX/2);
        int y1 = int(y - cos(fAngle) * kItemSizeY/2);
        polygon << QPoint(x1, y1);
    }

    return polygon;
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
         FizItem *item = fizitems[level][T+N/2][T+L+N/2];
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
    FizItem *it = fizitems[item_group[name]][T+N/2][T+L+N/2];
    item_group.remove(name);
    name = "";
    visible = false;
    it->name = "";
    invalidatePixmap();
    update();
    it->visible = false;
    return;
    }
    foreach (QString level, sysgroup.keys()) {
    FizItem *item = fizitems[level][T+N/2][T+L+N/2];
    if (item->name != "" && item_group[item->name] != item_group[name]) {
        //! Ошибка!
      fizitems[item_group.value(name)][T+N/2][T+L+N/2]->name = "";
      item_group.remove(name);
      name = item->name;
      this->level = item->level;
      G = item->G;
      k = item->k;
      visible = true;
      invalidatePixmap();
      update();
      break;
    }
  }
}

QDataStream &operator << (QDataStream &stream, const FizItem &elem)
{
    stream << elem.name << elem.symbol << elem.unit_of_measurement
           << elem.symbol_unit_of_measurement << elem.value_c <<
              elem.L << elem.T << elem.G << elem.k
           << elem.level << elem.visible
           // For backwards compat
           << 0 << 0;

    return stream;
}

QDataStream &operator >>(QDataStream &stream, FizItem &elem)
{
    int x=0, y=0;
    stream >> elem.name >> elem.symbol >> elem.unit_of_measurement
            >> elem.symbol_unit_of_measurement >> elem.value_c
            >> elem.L >> elem.T >> elem.G >> elem.k
           >> elem.level >> elem.visible
           // For backwards compat
           >> x >> y;
    return stream;
}
void FizItem::ClearCell()
{
    visible = false;
    selected = false;
    name = "";
}