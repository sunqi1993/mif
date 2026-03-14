// ResultList.qml - 结果列表组件
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    id: root
    spacing: 0
    
    property var model: []
    property var atPlugins: []
    property var pluginConfig: []
    property int modelCount: 0
    property int atPluginsCount: 0
    property int pluginConfigCount: 0
    property bool showAtPlugins: false
    property bool showConfig: false
    property int currentIndex: -1
    
    signal itemClicked(int index)
    signal atPluginClicked(string keyword)
    
    // @插件列表
    Column {
        visible: root.showAtPlugins && root.atPluginsCount > 0
        width: parent.width
        spacing: 0
        height: visible ? implicitHeight : 0
        
        SectionLabel {
            text: "可用插件  —  输入 @关键词 直接调用"
        }
        
        Repeater {
            model: root.atPlugins
            
            AtPluginItem {
                width: root.width - 30
                x: 15
                iconText: (root.atPlugins[index] && root.atPlugins[index].icon) || "🔌"
                atKeyword: (root.atPlugins[index] && root.atPlugins[index].at_keyword) || ""
                name: (root.atPlugins[index] && root.atPlugins[index].name) || ""
                description: (root.atPlugins[index] && root.atPlugins[index].description) || ""
                onClicked: root.atPluginClicked((root.atPlugins[index] && root.atPlugins[index].at_keyword) || "")
            }
        }
    }
    
    // 配置列表
    Column {
        visible: root.showConfig && root.pluginConfigCount > 0
        width: parent.width
        spacing: 0
        height: visible ? implicitHeight : 0
        
        SectionLabel {
            text: "当前配置"
        }
        
        Repeater {
            model: root.pluginConfig
            
            ConfigItem {
                width: root.width - 30
                x: 15
                optionName: (root.pluginConfig[index] && root.pluginConfig[index].name) || ""
                description: (root.pluginConfig[index] && root.pluginConfig[index].description) || ""
                typeHint: (root.pluginConfig[index] && root.pluginConfig[index].type_hint) || ""
                currentValue: (root.pluginConfig[index] && root.pluginConfig[index].current_value) || ""
            }
        }
    }
    
    // 普通结果列表
    Column {
        visible: !root.showAtPlugins && !root.showConfig && root.modelCount > 0
        width: parent.width
        spacing: 0
        height: visible ? implicitHeight : 0
        
        Repeater {
            model: root.model
            
            ResultItem {
                width: root.width - 30
                x: 15
                iconText: (root.model[index] && root.model[index].icon) || "🚀"
                title: (root.model[index] && root.model[index].title) || "[no title]"
                subtitle: (root.model[index] && root.model[index].subtitle) || ""
                onClicked: root.itemClicked(index)
            }
        }
    }
}