// SearchBar.qml - 搜索框组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    
    property string hintText: "搜索…"
    
    signal queryChanged(string query)
    signal submitted()
    
    radius: AppStyle.searchBorderRadius
    color: "#2a2a4a"  // 更明显的深色背景
    
    border.width: searchField.activeFocus ? 2 : 1
    border.color: searchField.activeFocus ? AppStyle.accent : "#3a3a5a"
    
    property alias inputText: searchField.text
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        spacing: 10
        
        // 搜索图标
        Text {
            text: "🔍"
            font.pixelSize: 18
            color: AppStyle.textTertiary
            Layout.alignment: Qt.AlignVCenter
        }
        
        // 输入框
        TextField {
            id: searchField
            Layout.fillWidth: true
            Layout.preferredHeight: parent.height - 10
            Layout.alignment: Qt.AlignVCenter
            
            placeholderText: root.hintText
            placeholderTextColor: "#9aa0b3"
            
            // 强制输入文字为白色，避免被系统样式覆盖成黄/主题色
            color: "#ffffff"
            palette.text: "#ffffff"
            palette.placeholderText: "#9aa0b3"
            selectionColor: "#4f8ef7"
            selectedTextColor: "#ffffff"
            font.pixelSize: AppStyle.fontSizeTitle
            font.weight: Font.Light
            verticalAlignment: TextInput.AlignVCenter
            
            background: null
            selectByMouse: true
            
            onTextChanged: root.queryChanged(text)
            onAccepted: root.submitted()
        }
    }
    
    // 聚焦动画
    Behavior on border.width {
        NumberAnimation { duration: 150 }
    }
    
    Behavior on border.color {
        ColorAnimation { duration: 150 }
    }
}