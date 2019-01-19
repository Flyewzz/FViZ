#ifndef GENERAL_SETTINGS_H
#define GENERAL_SETTINGS_H

#include <QWidget>
#include <QTimer>
#include "mainwindow.h"

namespace Ui {
class General_Settings;
}

class General_Settings : public QWidget
{
    Q_OBJECT
    QTimer *timer;
    int i_c;
public:
    explicit General_Settings(QWidget *parent = nullptr);
    ~General_Settings();

private:
    Ui::General_Settings *ui;
};

#endif // GENERAL_SETTINGS_H
