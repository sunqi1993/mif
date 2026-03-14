// ResultItem.qml - 结果项组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: parent ? parent.width : 0
    height: 56
    color: mouseArea.containsMouse ? "#ffffff0a" : "transparent"
    radius: AppStyle.borderRadiusSmall
    
    property string iconText: "🚀"
    property string title: ""
    property string subtitle: ""
    property bool isHovered: mouseArea.containsMouse
    
    signal clicked()
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: AppStyle.padding
        anchors.rightMargin: AppStyle.padding
        spacing: AppStyle.spacing
        
        // 图标
        Text {
            text: root.iconText
            font.pixelSize: 20
            Layout.alignment: Qt.AlignVCenter
        }
        
        // 文字内容
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: Math.max(80, root.width - 90)
            Layout.alignment: Qt.AlignVCenter
            spacing: 2
            
            Text {
                text: root.title
                // 强制高对比，避免主题/调色板导致文字与背景接近
                color: "#ffffff"
                font.pixelSize: AppStyle.fontSizeLarge
                font.weight: Font.Medium
                elide: Text.ElideRight
                Layout.fillWidth: true
                maximumLineCount: 1
                wrapMode: Text.NoWrap
                renderType: Text.NativeRendering
            }
            
            Text {
                visible: root.subtitle !== ""
                text: root.subtitle
                color: "#c7cfdf"
                font.pixelSize: AppStyle.fontSizeNormal
                elide: Text.ElideRight
                Layout.fillWidth: true
                maximumLineCount: 1
                wrapMode: Text.NoWrap
                renderType: Text.NativeRendering
            }
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: root.clicked()
    }
    
    // 悬停动画
    Behavior on color {
        ColorAnimation { duration: 100 }
    }
}