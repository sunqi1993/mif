// SectionLabel.qml - 分隔标签组件
import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    height: 30
    width: parent ? parent.width : 0
    
    property string text: ""
    
    Row {
        anchors.fill: parent
        anchors.leftMargin: AppStyle.padding
        anchors.rightMargin: AppStyle.padding
        spacing: 8
        
        Text {
            text: root.text
            color: AppStyle.textTertiary
            font.pixelSize: AppStyle.fontSizeSmall
            font.weight: Font.DemiBold
            anchors.verticalCenter: parent.verticalCenter
        }
        
        Rectangle {
            height: 1
            width: parent.width - 100
            color: AppStyle.divider
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}