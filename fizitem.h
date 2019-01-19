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
#include <QAbstractTextDocumentLayout>
#include "qmath.h"
#include "graphview.h"
#include "mainwindow.h"
#include <QWebEngineView>
#include "commands.h"

//Forward-declaration
class TextOut;

//Описание одного блока
class FizItem : public QGraphicsItem
{
    friend class GraphView;
    friend class AddElement;
    friend class Command_Element;
    friend class AddSysGroup;
    ///Убрать
    int x, y; //Координаты начала фигуры и ее размеры
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
    TextOut *tex;
    FizItem& operator = (const FizItem &another);
    friend QDataStream& operator << (QDataStream &stream, const FizItem &elem);
    friend QDataStream& operator >> (QDataStream &stream, FizItem &elem);
    //################
public:
    explicit FizItem(const qreal &x1, const qreal &y1, const int &l, const int &t, const QColor &col = Qt::black);
    ~FizItem();
    protected:
        virtual void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget);
        virtual QRectF boundingRect() const {
            return QRectF(x-57, y-56, 114, 113);
        }
    //Установка нового системного уровня
public:
   void setLevel(const int &a, const int &b);
   FizItem* operator =(const bool &exp) { visible = exp; return this; }
   void RemoveCell(); //Логическое удаление (в зависимости от количества элементов на данную соту)
   void ClearCell(); //Очистка блока
   void setVisible(const bool &);
   TextOut*& getTex() {return tex; }
   QString& getName() {return name;}
   void setSelect(const bool &flag); //Установка заданного выделения
   bool Select(); //Изменение выделения ячейки на противоположное (возврат результата bool)
};

QDataStream& operator << (QDataStream &stream, const FizItem &elem);
QDataStream& operator >> (QDataStream &stream, FizItem &elem);

class TextOut : public QWebEngineView {
 FizItem *parent;
 public:
    explicit TextOut(QWidget *pwrt = nullptr) : QWebEngineView(pwrt){ parent = nullptr; }
 void setParent(FizItem *& p);
 FizItem *& getParent();
};



#endif // FIZITEM_H
