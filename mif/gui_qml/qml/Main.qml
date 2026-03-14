// Main.qml - 主窗口
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "components"

Window {
    id: root
    visible: true
    width: AppStyle.windowWidth
    height: AppStyle.windowHeight
    color: AppStyle.bg
    flags: Qt.Window | Qt.WindowStaysOnTopHint
    
    title: "AlfredPy"
    
    // 信号：执行结果
    signal executeResult(int index)
    signal searchRequested(string query)
    signal atModeSelected(string keyword)
    signal exitAtMode()
    
    // 属性 - 绑定到 bridge
    property var results: bridge ? bridge.results : []
    property var atPlugins: bridge ? bridge.atPlugins : []
    property var pluginConfig: bridge ? bridge.pluginConfig : []
    property int resultsCount: bridge ? bridge.resultsCount : 0
    property int atPluginsCount: bridge ? bridge.atPluginsCount : 0
    property int pluginConfigCount: bridge ? bridge.pluginConfigCount : 0
    property string atKeyword: bridge ? bridge.atKeyword : ""
    property string atPluginName: bridge ? bridge.atPluginName : ""
    property string atPluginIcon: bridge ? bridge.atPluginIcon : ""
    property string atPluginHint: bridge ? bridge.atPluginHint : ""
    property bool isAtMode: bridge ? bridge.isAtMode : false
    property bool showCalcPanel: bridge ? bridge.showCalcPanel : false
    property string calcExpression: bridge ? bridge.calcExpression : ""
    property string calcResult: bridge ? bridge.calcResult : ""
    property string hintText: "搜索…  1+2  g Python  @calc  @wf  @settings"
    
    // 快捷键处理
    Shortcut {
        sequence: "Escape"
        onActivated: {
            if (root.isAtMode) {
                root.exitAtMode()
            } else {
                root.close()
            }
        }
    }
    
    Shortcut {
        sequence: "Return"
        onActivated: {
            if (resultList.currentIndex >= 0) {
                root.executeResult(resultList.currentIndex)
            }
        }
    }
    
    Shortcut {
        sequence: "Up"
        onActivated: resultList.decrementCurrentIndex()
    }
    
    Shortcut {
        sequence: "Down"
        onActivated: resultList.incrementCurrentIndex()
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // 搜索框区域
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 70
            color: AppStyle.bg
            
            SearchBar {
                id: searchBar
                anchors.fill: parent
                anchors.margins: AppStyle.padding
                hintText: root.hintText
                onQueryChanged: function(query) { root.searchRequested(query) }
                onSubmitted: {
                    if (resultList.currentIndex >= 0) {
                        root.executeResult(resultList.currentIndex)
                    }
                }
            }
        }
        
        // 结果区域
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: AppStyle.bg
            
            ScrollView {
                anchors.fill: parent
                clip: true
                
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AsNeeded
                
                Column {
                    id: resultContainer
                    width: parent.width
                    spacing: 6
                    
                    // @模式横幅
                    AtModeBanner {
                        visible: root.isAtMode
                        width: parent.width - 30
                        x: 15
                        pluginIcon: root.atPluginIcon
                        pluginName: root.atPluginName
                        atKeyword: root.atKeyword
                        hint: root.atPluginHint
                        onExitClicked: root.exitAtMode()
                    }
                    
                    // 计算器面板
                    CalcPanel {
                        visible: root.showCalcPanel
                        width: parent.width - 30
                        x: 15
                        expression: root.calcExpression
                        result: root.calcResult
                        onClicked: root.executeResult(0)
                    }
                    
                    // 结果列表
                    ResultList {
                        id: resultList
                        width: parent.width
                        model: root.results
                        modelCount: root.resultsCount
                        atPlugins: root.atPlugins
                        atPluginsCount: root.atPluginsCount
                        pluginConfig: root.pluginConfig
                        pluginConfigCount: root.pluginConfigCount
                        showAtPlugins: root.isAtMode && root.atPluginsCount > 0
                        showConfig: root.isAtMode && root.pluginConfigCount > 0
                        
                        onItemClicked: function(index) {
                            root.executeResult(index)
                        }
                        onAtPluginClicked: function(keyword) {
                            root.atModeSelected(keyword)
                        }
                    }
                    
                    // 空状态提示
                    Item {
                        visible: !root.isAtMode && root.resultsCount === 0 && !root.showCalcPanel
                        width: parent.width
                        height: 40
                        
                        Text {
                            anchors.centerIn: parent
                            text: "💡  输入 @ 查看所有可用插件"
                            color: AppStyle.textHint
                            font.pixelSize: AppStyle.fontSizeNormal
                        }
                    }
                }
            }
        }
    }
    
    // 公开方法
    function clearSearch() {
        searchBar.inputText = ""
    }
    
    function setSearchText(text) {
        searchBar.inputText = text
    }
    
    function focusSearch() {
        searchBar.forceActiveFocus()
    }
}