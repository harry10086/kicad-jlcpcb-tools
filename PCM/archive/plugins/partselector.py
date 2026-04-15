"""Contains the part selector modal window."""

import logging
import time

import wx  # pylint: disable=import-error
import wx.dataview as dv  # pylint: disable=import-error

from .datamodel import PartSelectorDataModel
from .derive_params import params_for_part  # pylint: disable=import-error
from .events import AssignPartsEvent, UpdateSetting
from .helpers import HighResWxSize, loadBitmapScaled
from .partdetails import PartDetailsDialog


class PartSelectorDialog(wx.Dialog):
    """The part selector window."""

    def __init__(self, parent, parts):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="JLCPCB 元件库",
            pos=wx.DefaultPosition,
            size=HighResWxSize(parent.window, wx.Size(1400, 800)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )

        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.parts = parts
        lcsc_selection = self.get_existing_selection(parts)

        self.search_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.search)

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
        # --------------------------- Search bar ------------------------------
        # ---------------------------------------------------------------------

        keyword_label = wx.StaticText(
            self,
            wx.ID_ANY,
            "Keywords",
            size=HighResWxSize(parent.window, wx.Size(65, 15)),
            style=wx.ALIGN_RIGHT,
        )
        self.keyword = wx.TextCtrl(
            self,
            wx.ID_ANY,
            lcsc_selection,
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(400, 24)),
            wx.TE_PROCESS_ENTER,
        )
        self.keyword.SetHint("e.g. 10k 0603")

        self.ohm_button = wx.Button(
            self,
            wx.ID_ANY,
            "Ω",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(20, -1)),
            0,
        )
        self.ohm_button.SetToolTip("Append the Ω symbol to the search string")

        self.micro_button = wx.Button(
            self,
            wx.ID_ANY,
            "µ",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(20, -1)),
            0,
        )
        self.micro_button.SetToolTip("Append the µ symbol to the search string")

        package_label = wx.StaticText(
            self,
            wx.ID_ANY,
            "Package",
            size=HighResWxSize(parent.window, wx.Size(55, 15)),
        )
        self.package = wx.ComboBox(
            self,
            wx.ID_ANY,
            "",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(150, 24)),
            style=wx.CB_DROPDOWN,
            name="package_filter",
        )
        self.package.SetHint("e.g. 0603")

        self.basic_checkbox = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Basic",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(60, 24)),
            0,
            name="basic",
        )
        self.extended_checkbox = wx.CheckBox(
            self,
            wx.ID_ANY,
            "Extended",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(80, 24)),
            0,
            name="extended",
        )
        stock_label = wx.StaticText(
            self,
            wx.ID_ANY,
            "Stock",
            size=HighResWxSize(parent.window, wx.Size(35, 15)),
        )
        self.stock_filter = wx.ComboBox(
            self,
            wx.ID_ANY,
            "All",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(80, 24)),
            choices=["All", ">0", ">10", ">100", ">1000"],
            style=wx.CB_READONLY,
            name="stock_filter",
        )

        self.basic_checkbox.SetValue(
            self.parent.settings.get("partselector", {}).get("basic", False)
        )
        self.extended_checkbox.SetValue(
            self.parent.settings.get("partselector", {}).get("extended", False)
        )
        stock_val = self.parent.settings.get("partselector", {}).get("stock_filter", "All")
        if stock_val in ["All", ">0", ">10", ">100", ">1000"]:
            self.stock_filter.SetValue(stock_val)

        self.basic_checkbox.Bind(wx.EVT_CHECKBOX, self.update_settings)
        self.extended_checkbox.Bind(wx.EVT_CHECKBOX, self.update_settings)
        self.stock_filter.Bind(wx.EVT_COMBOBOX, self.update_settings)
        self.package.Bind(wx.EVT_COMBOBOX, self.update_settings)
        self.package.Bind(wx.EVT_TEXT, self.update_settings)
        self.package.Bind(wx.EVT_TEXT_ENTER, self.search)



        self.search_button = wx.Button(
            self,
            wx.ID_ANY,
            "Search",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(100, -1)),
            0,
        )
        self.search_button.SetBitmap(
            loadBitmapScaled(
                "mdi-database-search-outline.png",
                self.parent.scale_factor,
            )
        )
        self.search_button.SetBitmapMargins((2, 0))

        keyword_search_row1 = wx.BoxSizer(wx.HORIZONTAL)
        keyword_search_row1.Add(keyword_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        keyword_search_row1.Add(
            self.keyword,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL,
            5,
        )
        keyword_search_row1.Add(
            self.ohm_button,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL,
            5,
        )
        keyword_search_row1.Add(
            self.micro_button,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL,
            5,
        )
        keyword_search_row1.Add(
            self.search_button,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL,
            5,
        )

        filter_row = wx.BoxSizer(wx.HORIZONTAL)
        filter_row.Add(package_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        filter_row.Add(self.package, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        filter_row.Add(self.basic_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        filter_row.Add(self.extended_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
        filter_row.Add(stock_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        filter_row.Add(self.stock_filter, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)

        search_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Search")
        search_sizer.Add(keyword_search_row1, 0, wx.EXPAND)
        search_sizer.Add(filter_row, 0, wx.EXPAND)

        self.keyword.Bind(wx.EVT_TEXT_ENTER, self.search)
        self.ohm_button.Bind(wx.EVT_BUTTON, self.add_ohm_symbol)
        self.micro_button.Bind(wx.EVT_BUTTON, self.add_micro_symbol)
        self.search_button.Bind(wx.EVT_BUTTON, self.search)


        # ---------------------------------------------------------------------
        # ------------------------ Result status line -------------------------
        # ---------------------------------------------------------------------

        self.result_count = wx.StaticText(
            self, wx.ID_ANY, "0 条结果", wx.DefaultPosition, wx.DefaultSize
        )
        
        self.load_more_button = wx.Button(
            self,
            wx.ID_ANY,
            "加载更多 (30)",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.load_more_button.Bind(wx.EVT_BUTTON, self.load_more)
        self.load_more_button.Disable()

        result_sizer = wx.BoxSizer(wx.HORIZONTAL)
        result_sizer.Add(self.result_count, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        result_sizer.Add(self.load_more_button, 0, wx.LEFT, 15)

        # ---------------------------------------------------------------------
        # ------------------------- Result Part list --------------------------
        # ---------------------------------------------------------------------

        table_sizer = wx.BoxSizer(wx.HORIZONTAL)

        table_scroller = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.VSCROLL)
        table_scroller.SetScrollRate(20, 20)

        self.part_list = dv.DataViewCtrl(
            table_scroller,
            style=wx.BORDER_THEME | dv.DV_ROW_LINES | dv.DV_VERT_RULES | dv.DV_SINGLE,
        )

        lcsc = self.part_list.AppendTextColumn(
            "LCSC",
            0,
            width=int(parent.scale_factor * 60),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_CENTER,
        )
        mfr_number = self.part_list.AppendTextColumn(
            "MFR Number",
            1,
            width=int(parent.scale_factor * 140),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )
        package = self.part_list.AppendTextColumn(
            "Package",
            2,
            width=int(parent.scale_factor * 100),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )
        pins = self.part_list.AppendTextColumn(
            "Pins",
            3,
            width=int(parent.scale_factor * 40),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_CENTER,
        )
        parttype = self.part_list.AppendTextColumn(
            "Type",
            4,
            width=int(parent.scale_factor * 50),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )
        params = self.part_list.AppendTextColumn(
            "Params",
            5,
            width=int(parent.scale_factor * 150),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_CENTER,
        )
        stock = self.part_list.AppendTextColumn(
            "Stock",
            6,
            width=int(parent.scale_factor * 50),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_CENTER,
        )
        mfr = self.part_list.AppendTextColumn(
            "Manufacturer",
            7,
            width=int(parent.scale_factor * 100),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )
        description = self.part_list.AppendTextColumn(
            "Description",
            8,
            width=int(parent.scale_factor * 300),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )
        price = self.part_list.AppendTextColumn(
            "Price",
            9,
            width=int(parent.scale_factor * 100),
            mode=dv.DATAVIEW_CELL_INERT,
            align=wx.ALIGN_LEFT,
        )

        lcsc.SetSortable(True)
        mfr_number.SetSortable(True)
        package.SetSortable(True)
        pins.SetSortable(True)
        parttype.SetSortable(True)
        params.SetSortable(True)
        stock.SetSortable(True)
        mfr.SetSortable(True)
        description.SetSortable(True)
        price.SetSortable(True)

        self.part_list.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnPartSelected)
        self.part_list.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.select_part)
        scrolled_sizer = wx.BoxSizer(wx.VERTICAL)
        scrolled_sizer.Add(self.part_list, 1, wx.EXPAND)
        table_scroller.SetSizer(scrolled_sizer)

        table_sizer.Add(table_scroller, 20, wx.ALL | wx.EXPAND, 5)

        # ---------------------------------------------------------------------
        # ------------------------ Right side toolbar -------------------------
        # ---------------------------------------------------------------------

        self.select_part_button = wx.Button(
            self,
            wx.ID_ANY,
            "选择元件",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(150, -1)),
            0,
        )
        self.part_details_button = wx.Button(
            self,
            wx.ID_ANY,
            "查看元件详情",
            wx.DefaultPosition,
            HighResWxSize(parent.window, wx.Size(150, -1)),
            0,
        )

        self.select_part_button.Bind(wx.EVT_BUTTON, self.select_part)
        self.part_details_button.Bind(wx.EVT_BUTTON, self.get_part_details)

        self.select_part_button.SetBitmap(
            loadBitmapScaled(
                "mdi-check.png",
                self.parent.scale_factor,
            )
        )
        self.select_part_button.SetBitmapMargins((2, 0))

        self.part_details_button.SetBitmap(
            loadBitmapScaled(
                "mdi-text-box-search-outline.png",
                self.parent.scale_factor,
            )
        )
        self.part_details_button.SetBitmapMargins((2, 0))

        tool_sizer = wx.BoxSizer(wx.VERTICAL)
        tool_sizer.Add(self.select_part_button, 0, wx.ALL, 5)
        tool_sizer.Add(self.part_details_button, 0, wx.ALL, 5)
        table_sizer.Add(tool_sizer, 3, wx.EXPAND, 5)

        # ---------------------------------------------------------------------
        # ------------------------------ Sizers  ------------------------------
        # ---------------------------------------------------------------------

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(search_sizer, 1, wx.ALL, 5)
        # layout.Add(self.search_button, 5, wx.ALL, 5)
        layout.Add(result_sizer, 1, wx.LEFT, 5)
        layout.Add(table_sizer, 20, wx.ALL | wx.EXPAND, 5)

        self.part_list_model = PartSelectorDataModel()
        self.part_list.AssociateModel(self.part_list_model)

        self.current_page = 1
        self.current_search_results = []
        
        self.SetSizer(layout)
        self.Layout()
        self.Centre(wx.BOTH)
        self.enable_toolbar_buttons(False)

        # initiate the initial search now that the window has been constructed
        self.search(None)

    def update_settings(self, event):
        """Update the settings on change."""
        wx.PostEvent(
            self.parent,
            UpdateSetting(
                section="partselector",
                setting=event.GetEventObject().GetName(),
                value=event.GetEventObject().GetValue(),
            ),
        )
        
        # Apply local filters instead of running network search
        self.apply_local_filters(0)

    @staticmethod
    def get_existing_selection(parts):
        """Check if exactly one LCSC part number is amongst the selected parts."""
        s = set(parts.values())
        if len(s) != 1:
            return ""
        return list(s)[0]

    def quit_dialog(self, *_):
        """Close this window."""
        self.Destroy()
        self.EndModal(0)

    def OnSortPartList(self, e):
        """Set order_by to the clicked column and trigger list refresh."""
        self.parent.library.set_order_by(e.GetColumn())
        self.search(None)

    def OnPartSelected(self, *_):
        """Enable the toolbar buttons when a selection was made."""
        if self.part_list.GetSelectedItemsCount() > 0:
            self.enable_toolbar_buttons(True)
        else:
            self.enable_toolbar_buttons(False)

    def enable_toolbar_buttons(self, state):
        """Control the state of all the buttons in toolbar on the right side."""
        for b in [
            self.select_part_button,
            self.part_details_button,
        ]:
            b.Enable(bool(state))

    def add_ohm_symbol(self, *_):
        """Append the Ω symbol to the search string."""
        self.keyword.AppendText("Ω")

    def add_micro_symbol(self, *_):
        """Append the µ symbol to the search string."""
        self.keyword.AppendText("µ")

    def search_dwell(self, *_):
        """Initiate a search once the timeout expires."""
        self.search_timer.StartOnce(750)

    def load_more(self, event):
        """Load the next page of results."""
        self.current_page += 1
        self._do_search()

    def search(self, *_):
        """Reset state and perform a new search."""
        self.current_page = 1
        self.current_search_results = []
        self._do_search()

    def _do_search(self):
        """Perform the actual search and update the local state."""
        parameters = {
            "keyword": self.keyword.GetValue(),
            "package": self.package.GetValue(),
        }
        
        self.result_count.SetLabel("加载中...")
        self.Update()

        start = time.time()
        use_szlcsc_online = self.parent.settings.get("general", {}).get("szlcsc_online_search", True)
        
        new_results = []
        if use_szlcsc_online:
            if self.current_page == 1:
                res1 = self.parent.library.search(parameters, page=1)
                res2 = self.parent.library.search(parameters, page=2)
                new_results = res1 + res2
                self.current_page = 2
            else:
                new_results = self.parent.library.search(parameters, page=self.current_page)
             
            if new_results:
                self.load_more_button.Enable()
            else:
                self.load_more_button.Disable()
        else:
            self.load_more_button.Disable()
            new_results = self.parent.library.search(parameters)

        self.current_search_results.extend(new_results)
        
        # Auto-update package combobox
        current_pkg = self.package.GetValue()
        unique_packages = sorted(list(set(item[2] for item in self.current_search_results if len(item) > 2 and item[2])))
        self.package.Clear()
        self.package.AppendItems([""] + unique_packages)
        self.package.SetValue(current_pkg)
        
        search_duration = time.time() - start
        
        self.apply_local_filters(search_duration)

    def apply_local_filters(self, search_duration):
        """Apply local filtering conditions based on checkboxes and combo boxes."""
        basic = self.basic_checkbox.GetValue()
        extended = self.extended_checkbox.GetValue()
        stock_filter_str = self.stock_filter.GetValue()
        package_filter = self.package.GetValue().lower()
        
        min_stock = 0
        if stock_filter_str == ">0":
            min_stock = 1
        elif stock_filter_str == ">10":
            min_stock = 11
        elif stock_filter_str == ">100":
            min_stock = 101
        elif stock_filter_str == ">1000":
            min_stock = 1001
        
        filtered = []
        
        for item in self.current_search_results:
            
            # Type is at index 4, Stock is at index 5, Package is at index 2
            if len(item) < 6:
                continue
                
            item_package = item[2].lower() if item[2] else ""
            item_type = item[4]
            stock_str = item[5]
            try:
                item_stock = int(stock_str)
            except ValueError:
                item_stock = 0
                
            if item_stock < min_stock:
                continue
                
            if package_filter and package_filter not in item_package:
                continue
                
            if basic and not extended and item_type != "Basic":
                continue
            if extended and not basic and item_type != "Extended":
                continue
            if basic and extended and item_type not in ("Basic", "Extended"):
                continue
                
            filtered.append(item)
            
        self.populate_part_list(filtered, search_duration)

    def get_price(self, quantity, prices) -> float:
        """Find the price for the number of selected parts accordning to the price ranges."""
        if not prices:
            return -1.0
        
        # Check if the price is a single scalar from the online API instead of a range string
        if ":" not in prices and "-" not in prices:
            try:
                return float(prices)
            except ValueError:
                return -1.0
                
        price_ranges = prices.split(",")
        if not price_ranges[0]:
            return -1.0
        min_quantity = int(price_ranges[0].split("-")[0])
        if quantity <= min_quantity:
            range, price = price_ranges[0].split(":")
            return float(price)
        for p in price_ranges:
            range, price = p.split(":")
            lower, upper = range.split("-")
            if not upper:  # upper bound of price ranges
                return float(price)
            lower = int(lower)
            upper = int(upper)
            if lower <= quantity < upper:
                return float(price)
        return -1.0

    def populate_part_list(self, parts, search_duration):
        """Populate the list with the result of the search."""
        search_duration_text = (
            f"{search_duration:.2f}s"
            if search_duration > 1
            else f"{search_duration * 1000.0:.0f}ms"
        )
        self.part_list_model.RemoveAll()
        if parts is None:
            return
        count = len(parts)
        if count >= 1000:
            self.result_count.SetLabel(
                f"{count} 条结果 (已限制) 用时 {search_duration_text}"
            )
        else:
            self.result_count.SetLabel(f"{count} 条结果 用时 {search_duration_text}")
        for p in parts:
            item = [str(c) for c in p]
            pricecol = 8  # Must match order in library.py search function
            price = round(self.get_price(len(self.parts), item[pricecol]), 3)
            if price > 0:
                sum = round(price * len(self.parts), 3)
                item[pricecol] = (
                    f"{len(self.parts)} 个元件: 单价 ¥{price} / 合计 ¥{sum}"
                )
            else:
                item[pricecol] = "价格数据错误"
            params = item[7]
            item.insert(5, params)
            self.part_list_model.AddEntry(item)

    def select_part(self, *_):
        """Save the selected part number and close the modal."""
        if self.part_list.GetSelectedItemsCount() > 0:
            item = self.part_list.GetSelection()
            wx.PostEvent(
                self.parent,
                AssignPartsEvent(
                    lcsc=self.part_list_model.get_lcsc(item),
                    type=self.part_list_model.get_type(item),
                    stock=self.part_list_model.get_stock(item),
                    params=self.part_list_model.get_params(item),
                    references=self.parts.keys(),
                ),
            )
            self.EndModal(wx.ID_OK)

    def get_part_details(self, *_):
        """Fetch part details from LCSC and show them in a modal."""
        if self.part_list.GetSelectedItemsCount() > 0:
            item = self.part_list.GetSelection()
            busy_cursor = wx.BusyCursor()
            url = self.part_list_model.get_url(item)
            datasheet = self.part_list_model.get_datasheet(item)
            dialog = PartDetailsDialog(self.parent, self.part_list_model.get_lcsc(item), url, datasheet)
            del busy_cursor
            dialog.ShowModal()

