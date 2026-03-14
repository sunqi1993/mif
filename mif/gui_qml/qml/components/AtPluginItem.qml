// AtPluginItem.qml - @插件列表项组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    height: 56
    color: mouseArea.containsMouse ? "#ffffff0a" : "transparent"
    radius: AppStyle.borderRadiusSmall
    
    property string iconText: "🔌"
    property string atKeyword: ""
    property string name: ""
    property string description: ""
    
    signal clicked()
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: AppStyle.padding
        anchors.rightMargin: AppStyle.padding
        spacing: AppStyle.spacing
        
        // 图标
        Text {
            text: root.iconText
            font.pixelSize: 22
            Layout.alignment: Qt.AlignVCenter
        }
        
        // 文字内容
        Column {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 2
            
            Row {
                spacing: 0
                Text {
                    text: "@" + root.atKeyword
                    color: "#ffb020"
                    font.pixelSize: AppStyle.fontSizeLarge
                    font.weight: Font.DemiBold
                }
                Text {
                    text: "  " + root.name
                    color: "#ffffff"
                    font.pixelSize: AppStyle.fontSizeLarge
                }
            }
            
            Text {
                text: root.description
                color: "#c7cfdf"
                font.pixelSize: AppStyle.fontSizeNormal
                elide: Text.ElideRight
                width: parent.width
            }
        }
        
        // 提示
        Text {
            text: "↩ 选择"
            color: AppStyle.textHint
            font.pixelSize: AppStyle.fontSizeNormal
            Layout.alignment: Qt.AlignVCenter
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: root.clicked()
    }
    
    Behavior on color {
        ColorAnimation { duration: 100 }
    }
}