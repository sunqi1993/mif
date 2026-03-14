// ConfigItem.qml - 配置项组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    height: 60
    color: "transparent"
    radius: AppStyle.borderRadiusSmall
    
    property string optionName: ""
    property string description: ""
    property string typeHint: ""
    property string currentValue: ""
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: AppStyle.padding
        anchors.rightMargin: AppStyle.padding
        spacing: AppStyle.spacing
        
        Column {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 2
            
            Text {
                text: root.optionName
                color: AppStyle.textPrimary
                font.pixelSize: AppStyle.fontSizeMedium
                font.weight: Font.Medium
            }
            
            Text {
                visible: root.description !== ""
                text: root.description
                color: AppStyle.textTertiary
                font.pixelSize: AppStyle.fontSizeNormal
                elide: Text.ElideRight
                width: parent.width
            }
            
            Text {
                visible: root.typeHint !== ""
                text: root.typeHint
                color: AppStyle.textHint
                font.pixelSize: AppStyle.fontSizeSmall
            }
        }
        
        // 当前值
        Text {
            text: root.currentValue
            color: AppStyle.accentWarm
            font.pixelSize: AppStyle.fontSizeMedium
            font.weight: Font.DemiBold
            Layout.alignment: Qt.AlignVCenter
        }
    }
}