// CalcPanel.qml - 计算器面板组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    height: contentColumn.height + 28
    color: AppStyle.bgCalc
    radius: AppStyle.borderRadius
    
    property string expression: ""
    property string result: ""
    
    signal clicked()
    
    border.width: 1
    border.color: AppStyle.accentDim
    
    Column {
        id: contentColumn
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: AppStyle.padding
        spacing: 0
        
        // 标题行
        Row {
            spacing: 6
            Text {
                text: "🧮"
                font.pixelSize: 16
            }
            Text {
                text: "计算器"
                color: AppStyle.accent
                font.pixelSize: 11
                font.weight: Font.DemiBold
            }
        }
        
        // 表达式
        Text {
            text: root.expression
            color: AppStyle.textSecondary
            font.pixelSize: AppStyle.fontSizeMedium
            font.family: AppStyle.fontMono
            elide: Text.ElideRight
            width: parent.width
            topPadding: 6
        }
        
        // 结果
        Text {
            text: root.result
            color: AppStyle.textPrimary
            font.pixelSize: AppStyle.fontSizeDisplay
            font.weight: Font.Bold
            font.family: AppStyle.fontMono
            topPadding: 4
            bottomPadding: 6
        }
        
        // 提示
        Text {
            text: "↩  点击或按 Enter 复制到剪贴板"
            color: AppStyle.textTertiary
            font.pixelSize: AppStyle.fontSizeNormal
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: root.clicked()
    }
}