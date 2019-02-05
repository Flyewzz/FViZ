#ifndef FIZITEM_H
#define FIZITEM_H

#include <QPainter>
#include <QColor>
#include <QFont>
#include <QGraphicsScene>
#include <QGraphicsWidget>
#include <QVector>
#include <QString>
#include <QTextDocument>
#include <QPolygon>
#include <QAbstractTextDocumentLayout>
#include "qmath.h"
#include "graphview.h"
#include "mainwindow.h"
#include <QWebEngineView>
#include "commands.h"

//Forward-declaration
class TextOut;
class RenderFizitem;
extern int N;

//Описание одного блока
class FizItem : public QGraphicsItem
{
    friend class GraphView;
    friend class AddElement;
    friend class Command_Element;
    friend class AddSysGroup;
    friend class RenderFizitem;

    QString name; //Название блока
    QString symbol; //Условное обозначение
    QString unit_of_measurement; //Единица измерения
    QString symbol_unit_of_measurement; //Обозначение единицы измерения
    bool selected;
    int L; //Координата пути
    int T; //Координата времени
    //Уровень
    int G;
    int k;
    QString value_c; // Размерность в СИ
    bool visible;
    QColor level; //Уровень

    QPixmap cachedPixmap;
    bool pixmapOutdated = true;
    quint64 renderRequest = 0;

    static constexpr const double kItemSizeScale = 1.5;
    static constexpr const double kTextScale = 1.3;

    static constexpr const int kItemSizeX = 130*kItemSizeScale;
    static constexpr const int kItemSizeY = 110*kItemSizeScale;

    static constexpr const int kTextSizeX = 100*kItemSizeScale;
    static constexpr const int kTextSizeY =  90*kItemSizeScale;

    static constexpr const int kItemStepX =  60*kItemSizeScale;
    static constexpr const int kItemStepY =  90*kItemSizeScale;

    static constexpr const int kPolygonN  = 6;

    FizItem& operator = (const FizItem &another);
    friend QDataStream& operator << (QDataStream &stream, const FizItem &elem);
    friend QDataStream& operator >> (QDataStream &stream, FizItem &elem);
    //################
public:
    explicit FizItem(const int l, const int t, const QColor &col = Qt::black);
    ~FizItem();
protected:
    virtual void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget) override;

    virtual QRectF boundingRect() const override {
        return QRectF(xPos()-kItemSizeX/2, yPos()-kItemSizeY/2, kItemSizeX, kItemSizeY);
    }

    QPolygon boundingPolygon() const;

    virtual QPainterPath shape() const override {
        QPainterPath path;
        path.addPolygon(boundingPolygon());
        return path;
    }
    //Установка нового системного уровня
public:
   void setLevel(const int &a, const int &b);
   FizItem* operator =(const bool &exp) { visible = exp; return this; }
    FizItem& assign(const FizItem &rhs) {
        this->level = rhs.level;
        this->name = rhs.name;
        this->G = rhs.G;
        this->k = rhs.k;
        this->symbol = rhs.symbol;
        this->value_c = rhs.value_c;
        this->unit_of_measurement = rhs.unit_of_measurement;
        this->symbol_unit_of_measurement = rhs.symbol_unit_of_measurement;
        this->pixmapOutdated = rhs.pixmapOutdated;
        if (!this->pixmapOutdated) {
            this->cachedPixmap = rhs.cachedPixmap;
        }
        return *this;
    }
    void RemoveCell(); //Логическое удаление (в зависимости от количества элементов на данную соту)
    void ClearCell(); //Очистка блока

    const QString& getName() const {
        return name;
    }

    void setVisible(const bool v) {
        visible = v;
        update();
    }

    //Установка заданного выделения
    void setSelect(const bool flag) {
        selected = flag;
        update();
    }

    //Изменение выделения ячейки на противоположное (возврат результата bool)
    bool Select() {
        selected = !selected;
        update();
        return selected;
    }

    int xPos() const {
        return scene()->width()/2 + (L - T)*kItemStepX - (N/2)*kItemStepX;
    };
    int yPos() const {
        return scene()->height()/2 - (L + T)*kItemStepY;
    };

    void setPixmap(const QPixmap& pm) {
        cachedPixmap = pm;
        pixmapOutdated = false;
    }

    void invalidatePixmap();
};

QDataStream& operator << (QDataStream &stream, const FizItem &elem);
QDataStream& operator >> (QDataStream &stream, FizItem &elem);


#endif // FIZITEM_H
