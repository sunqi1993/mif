// AtModeBanner.qml - @模式横幅组件
import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: parent ? parent.width : 0
    height: 56
    color: "#1a1200"
    radius: 10
    
    property string pluginIcon: "🔌"
    property string pluginName: ""
    property string atKeyword: ""
    property string hint: ""
    
    signal exitClicked()
    
    border.width: 1
    border.color: "#3a2800"
    
    Text {
        id: iconText
        text: root.pluginIcon
        font.pixelSize: 18
        anchors.left: parent.left
        anchors.leftMargin: 15
        anchors.verticalCenter: parent.verticalCenter
    }

    Rectangle {
        id: exitBtn
        anchors.right: parent.right
        anchors.rightMargin: 15
        anchors.verticalCenter: parent.verticalCenter
        width: exitText.width + 12
        height: 26
        radius: 4
        color: exitMouseArea.containsMouse ? "#3a3a5a" : "transparent"

        Text {
            id: exitText
            anchors.centerIn: parent
            text: "× 退出"
            color: "#d6d9e2"
            font.pixelSize: 12
        }

        MouseArea {
            id: exitMouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.exitClicked()
        }
    }

    Column {
        anchors.left: iconText.right
        anchors.leftMargin: 10
        anchors.right: exitBtn.left
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        spacing: 2

        Text {
            text: "@" + root.atKeyword + "  —  " + root.pluginName + " 模式"
            color: "#ffb020"
            font.pixelSize: 13
            font.weight: Font.DemiBold
            elide: Text.ElideRight
            width: parent.width
            maximumLineCount: 1
        }

        Text {
            visible: root.hint !== ""
            text: root.hint
            color: "#d6d9e2"
            font.pixelSize: 12
            elide: Text.ElideRight
            width: parent.width
            maximumLineCount: 1
        }
    }
}