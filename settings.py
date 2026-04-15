"""Contains the settings dialog."""

import logging

import wx  # pylint: disable=import-error

from .events import UpdateSetting
from .helpers import HighResWxSize, loadBitmapScaled


class SettingsDialog(wx.Dialog):
    """Dialog for plugin settings."""

    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="JLCPCB 工具设置",
            pos=wx.DefaultPosition,
            size=HighResWxSize(parent.window, wx.Size(1300, 800)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )

        self.logger = logging.getLogger(__name__)
        self.parent = parent

        # ---------------------------------------------------------------------
        # ---------------------------- Hotkeys --------------------------------
        # ---------------------------------------------------------------------
        quitid = wx.NewId()
        self.Bind(wx.EVT_MENU, self.quit_dialog, id=quitid)

        entries = [wx.AcceleratorEntry(), wx.AcceleratorEntry(), wx.AcceleratorEntry()]
        entries[0].Set(wx.ACCEL_CTRL, ord("W"), quitid)
        entries[1].Set(wx.ACCEL_CTRL, ord("Q"), quitid)
        entries[2].Set(wx.ACCEL_SHIFT, wx.WXK_ESCAPE, quitid)
        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        # ---------------------------------------------------------------------
        # ------------------------- Change settings ---------------------------
        # ---------------------------------------------------------------------

        ##### Tented vias #####

        self.tented_vias_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="不覆盖过孔",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="gerber_tented_vias",
        )

        self.tented_vias_setting.SetToolTip(
            wx.ToolTip("过孔是否应被阻组层覆盖")
        )

        self.tented_vias_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("tented.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.tented_vias_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        tented_vias_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tented_vias_sizer.Add(self.tented_vias_image, 10, wx.ALL | wx.EXPAND, 5)
        tented_vias_sizer.Add(self.tented_vias_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Fill zones #####

        self.fill_zones_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="填充区域",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="gerber_fill_zones",
        )

        self.fill_zones_setting.SetToolTip(
            wx.ToolTip("生成 Gerber 时是否填充区域")
        )

        self.fill_zones_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("fill-zones.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.fill_zones_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        fill_zones_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fill_zones_sizer.Add(self.fill_zones_image, 10, wx.ALL | wx.EXPAND, 5)
        fill_zones_sizer.Add(self.fill_zones_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Plot values #####

        self.plot_values_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="绘制值",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="gerber_plot_values",
        )

        self.plot_values_setting.SetToolTip(
            wx.ToolTip("生成 Gerber 时是否绘制值")
        )

        self.plot_values_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("plot_values.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.plot_values_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        plot_values_sizer = wx.BoxSizer(wx.HORIZONTAL)
        plot_values_sizer.Add(self.plot_values_image, 10, wx.ALL | wx.EXPAND, 5)
        plot_values_sizer.Add(self.plot_values_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Plot references #####

        self.plot_references_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="绘制位号",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="gerber_plot_references",
        )

        self.plot_references_setting.SetToolTip(
            wx.ToolTip("生成 Gerber 时是否绘制位号")
        )

        self.plot_references_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("plot_refs.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.plot_references_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        plot_references_sizer = wx.BoxSizer(wx.HORIZONTAL)
        plot_references_sizer.Add(self.plot_references_image, 10, wx.ALL | wx.EXPAND, 5)
        plot_references_sizer.Add(
            self.plot_references_setting, 100, wx.ALL | wx.EXPAND, 5
        )

        ##### LCSC priority #####

        self.lcsc_priority_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="LCSC 编号优先级",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="general_lcsc_priority",
        )

        self.lcsc_priority_setting.SetToolTip(
            wx.ToolTip(
                "原理图中的 LCSC 编号是否优先于数据库中的"
            )
        )

        self.lcsc_priority_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("schematic.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.lcsc_priority_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        lcsc_priority_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lcsc_priority_sizer.Add(self.lcsc_priority_image, 10, wx.ALL | wx.EXPAND, 5)
        lcsc_priority_sizer.Add(self.lcsc_priority_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Only parts with LCSC number in BOM/CPL #####

        self.lcsc_bom_cpl_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="将无 LCSC 编号的元件添加到 BOM/CPL",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="gerber_lcsc_bom_cpl",
        )

        self.lcsc_bom_cpl_setting.SetToolTip(
            wx.ToolTip("无 LCSC 编号的元件是否应添加到 BOM/CPL")
        )

        self.lcsc_bom_cpl_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("bom.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.lcsc_bom_cpl_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        lcsc_bom_cpl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lcsc_bom_cpl_sizer.Add(self.lcsc_bom_cpl_image, 10, wx.ALL | wx.EXPAND, 5)
        lcsc_bom_cpl_sizer.Add(self.lcsc_bom_cpl_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Check if order/serial number placeholder is present #####

        self.order_number_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="检查是否放置了订单号/序列号占位符",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="general_order_number",
        )

        self.order_number_setting.SetToolTip(
            wx.ToolTip("是否放置了订单号/序列号占位符")
        )

        self.order_number_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("order_number.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.order_number_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        order_number_sizer = wx.BoxSizer(wx.HORIZONTAL)
        order_number_sizer.Add(self.order_number_image, 10, wx.ALL | wx.EXPAND, 5)
        order_number_sizer.Add(self.order_number_setting, 100, wx.ALL | wx.EXPAND, 5)

        ##### Use SZLCSC online search #####

        self.szlcsc_online_search_setting = wx.CheckBox(
            self,
            id=wx.ID_ANY,
            label="使用立创商城在线搜索",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=0,
            name="general_szlcsc_online_search",
        )

        self.szlcsc_online_search_setting.SetToolTip(
            wx.ToolTip("是否使用立创商城在线数据库搜索元件")
        )

        self.szlcsc_online_search_image = wx.StaticBitmap(
            self,
            wx.ID_ANY,
            loadBitmapScaled("mdi-database-search-outline.png", self.parent.scale_factor, static=True),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )

        self.szlcsc_online_search_setting.Bind(wx.EVT_CHECKBOX, self.update_settings)

        szlcsc_online_search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        szlcsc_online_search_sizer.Add(self.szlcsc_online_search_image, 10, wx.ALL | wx.EXPAND, 5)
        szlcsc_online_search_sizer.Add(self.szlcsc_online_search_setting, 100, wx.ALL | wx.EXPAND, 5)

        # ---------------------------------------------------------------------
        # ---------------------- Main Layout Sizer ----------------------------
        # ---------------------------------------------------------------------

        layout = wx.GridSizer(10, 2, 0, 0)
        layout.Add(tented_vias_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(fill_zones_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(plot_values_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(plot_references_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(lcsc_priority_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(lcsc_bom_cpl_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(order_number_sizer, 0, wx.ALL | wx.EXPAND, 5)
        layout.Add(szlcsc_online_search_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(layout)
        self.Layout()
        self.Centre(wx.BOTH)

        self.load_settings()

    def update_tented_vias(self, tented):
        """Update settings dialog according to the settings."""
        if tented:
            self.tented_vias_setting.SetValue(tented)
            self.tented_vias_setting.SetLabel("覆盖过孔")
            self.tented_vias_image.SetBitmap(
                loadBitmapScaled("tented.png", self.parent.scale_factor, static=True)
            )
        else:
            self.tented_vias_setting.SetValue(tented)
            self.tented_vias_setting.SetLabel("不覆盖过孔")
            self.tented_vias_image.SetBitmap(
                loadBitmapScaled("untented.png", self.parent.scale_factor, static=True)
            )

    def update_fill_zones(self, fill):
        """Update settings dialog according to the settings."""
        if fill:
            self.fill_zones_setting.SetValue(fill)
            self.fill_zones_setting.SetLabel("填充区域")
            self.fill_zones_image.SetBitmap(
                loadBitmapScaled(
                    "fill-zones.png", self.parent.scale_factor, static=True
                )
            )
        else:
            self.fill_zones_setting.SetValue(fill)
            self.fill_zones_setting.SetLabel("不填充区域")
            self.fill_zones_image.SetBitmap(
                loadBitmapScaled(
                    "unfill-zones.png", self.parent.scale_factor, static=True
                )
            )

    def update_plot_values(self, plot_values):
        """Update settings dialog according to the settings."""
        if plot_values:
            self.plot_values_setting.SetValue(plot_values)
            self.plot_values_setting.SetLabel("在丝印层绘制值")
            self.plot_values_image.SetBitmap(
                loadBitmapScaled(
                    "plot_values.png", self.parent.scale_factor, static=True
                )
            )
        else:
            self.plot_values_setting.SetValue(plot_values)
            self.plot_values_setting.SetLabel("不在丝印层绘制值")
            self.plot_values_image.SetBitmap(
                loadBitmapScaled("no_values.png", self.parent.scale_factor, static=True)
            )

    def update_plot_references(self, plot_references):
        """Update settings dialog according to the settings."""
        if plot_references:
            self.plot_references_setting.SetValue(plot_references)
            self.plot_references_setting.SetLabel("在丝印层绘制位号")
            self.plot_references_image.SetBitmap(
                loadBitmapScaled("plot_refs.png", self.parent.scale_factor, static=True)
            )
        else:
            self.plot_references_setting.SetValue(plot_references)
            self.plot_references_setting.SetLabel("不在丝印层绘制位号")
            self.plot_references_image.SetBitmap(
                loadBitmapScaled("no_refs.png", self.parent.scale_factor, static=True)
            )

    def update_lcsc_priority(self, priority):
        """Update settings dialog according to the settings."""
        if priority:
            self.lcsc_priority_setting.SetValue(priority)
            self.lcsc_priority_setting.SetLabel(
                "原理图的 LCSC 编号优先"
            )
            self.lcsc_priority_image.SetBitmap(
                loadBitmapScaled("schematic.png", self.parent.scale_factor, static=True)
            )
        else:
            self.lcsc_priority_setting.SetValue(priority)
            self.lcsc_priority_setting.SetLabel(
                "数据库的 LCSC 编号优先"
            )
            self.lcsc_priority_image.SetBitmap(
                loadBitmapScaled(
                    "database-outline.png", self.parent.scale_factor, static=True
                )
            )

    def update_lcsc_bom_cpl(self, add):
        """Update settings dialog according to the settings."""
        if add:
            self.lcsc_bom_cpl_setting.SetValue(add)
            self.lcsc_bom_cpl_setting.SetLabel(
                "将无 LCSC 编号的元件添加到 BOM/POS"
            )
            self.lcsc_bom_cpl_image.SetBitmap(
                loadBitmapScaled("bom.png", self.parent.scale_factor, static=True)
            )
        else:
            self.lcsc_bom_cpl_setting.SetValue(add)
            self.lcsc_bom_cpl_setting.SetLabel(
                "不将无 LCSC 编号的元件添加到 BOM/POS"
            )
            self.lcsc_bom_cpl_image.SetBitmap(
                loadBitmapScaled("no_bom.png", self.parent.scale_factor, static=True)
            )

    def update_order_number(self, check):
        """Update settings dialog according to the settings."""
        self.logger.debug(check)
        if check:
            self.order_number_setting.SetValue(check)
            self.order_number_setting.SetLabel(
                "检查是否放置了订单号/序列号占位符"
            )
            self.order_number_image.SetBitmap(
                loadBitmapScaled(
                    "order_number.png", self.parent.scale_factor, static=True
                )
            )
        else:
            self.order_number_setting.SetValue(check)
            self.order_number_setting.SetLabel(
                "不检查订单号/序列号占位符"
            )
            self.order_number_image.SetBitmap(
                loadBitmapScaled(
                    "no_order_number.png", self.parent.scale_factor, static=True
                )
            )

    def update_szlcsc_online_search(self, use_online):
        """Update settings dialog according to the settings."""
        if use_online:
            self.szlcsc_online_search_setting.SetValue(use_online)
            self.szlcsc_online_search_setting.SetLabel(
                "使用立创商城在线搜索"
            )
            self.szlcsc_online_search_image.SetBitmap(
                loadBitmapScaled("mdi-database-search-outline.png", self.parent.scale_factor, static=True)
            )
        else:
            self.szlcsc_online_search_setting.SetValue(use_online)
            self.szlcsc_online_search_setting.SetLabel(
                "使用离线 SQLite 数据库"
            )
            self.szlcsc_online_search_image.SetBitmap(
                loadBitmapScaled(
                    "database-outline.png", self.parent.scale_factor, static=True
                )
            )

    def load_settings(self):
        """Load settings and set checkboxes accordingly."""
        self.update_tented_vias(
            self.parent.settings.get("gerber", {}).get("tented_vias", True)
        )
        self.update_fill_zones(
            self.parent.settings.get("gerber", {}).get("fill_zones", True)
        )
        self.update_plot_values(
            self.parent.settings.get("gerber", {}).get("plot_values", True)
        )
        self.update_plot_references(
            self.parent.settings.get("gerber", {}).get("plot_references", True)
        )
        self.update_lcsc_priority(
            self.parent.settings.get("general", {}).get("lcsc_priority", True)
        )
        self.update_lcsc_bom_cpl(
            self.parent.settings.get("gerber", {}).get("lcsc_bom_cpl", True)
        )
        self.update_order_number(
            self.parent.settings.get("general", {}).get("order_number", True)
        )
        self.update_szlcsc_online_search(
            self.parent.settings.get("general", {}).get("szlcsc_online_search", True)
        )

    def update_settings(self, event):
        """Update and persist a setting that was changed."""
        section, name = event.GetEventObject().GetName().split("_", 1)
        value = event.GetEventObject().GetValue()
        self.logger.debug(section)
        self.logger.debug(name)
        self.logger.debug(value)
        getattr(self, f"update_{name}")(value)

        wx.PostEvent(
            self.parent,
            UpdateSetting(
                section=section,
                setting=name,
                value=value,
            ),
        )

    def quit_dialog(self, *_):
        """Close this dialog."""
        self.Destroy()
        self.EndModal(0)
