#include "mainwindow.h"
#include <QApplication>
#include <QtGui>
#include <QSplashScreen>

/*
void loadModules(QSplashScreen *splash) {
    QTime time;
    time.start();
    for (int i = 0; i < 100; ) {
        if (time.elapsed() > 40) {time.start(); ++i;}
        splash->showMessage(QString("Загрузка: %1%").arg(i),
                            Qt::AlignHCenter | Qt::AlignBottom | Qt::black);
    }
}
*/
int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    /*
    QSplashScreen splash;
    splash.show();
    QLabel lbl("<h1><center>FViZ 1.0 beta загружен!</center></h1>");
    loadModules(&splash);
    splash.finish(&lbl);
    lbl.resize(500, 250);
    lbl.show();
*/

    MainWindow w;
    w.setWindowIcon(QIcon(":/pics/pics/main_icon.png"));
    w.show();
    return a.exec();
}
