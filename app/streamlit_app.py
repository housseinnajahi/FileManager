import datetime
import os

import streamlit as st
from files import FileManager
from st_ant_tree import st_ant_tree
from streamlit_echarts import st_echarts

WORK_DIR = os.environ.get("WORK_DIR")


file_manager = FileManager(WORK_DIR)


def intro():
    import streamlit as st

    st.write("# Welcome to File Manager! 👋")

    data = file_manager.get_nb_size_files_by_directories()
    options = {
        "xAxis": {
            "type": "category",
            "data": data["directory"],
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data["count"], "type": "bar"}],
        "title": [
            {"text": "Number of files by directory", "top": "bottom", "left": "center"}
        ],
    }
    st_echarts(options=options)
    options = {
        "xAxis": {
            "type": "category",
            "data": data["directory"],
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data["size"], "type": "bar"}],
        "title": [
            {"text": "Size of files by directory Mo", "top": "bottom", "left": "center"}
        ],
    }
    st_echarts(options=options)
    data, directories = file_manager.get_data_by_date()
    option = {
        "title": {
            "text": "Size of files added by date",
            "top": "bottom",
            "left": "center",
        },
        "legend": {"data": directories},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {"type": "category", "boundaryGap": False, "data": data["dates"]},
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": directory,
                "type": "line",
                "stack": "Total",
                "data": data["directories"][directory]["size"],
            }
            for directory in data["directories"]
        ],
    }
    st_echarts(options=option)
    option = {
        "title": {
            "text": "Number of files added by date",
            "top": "bottom",
            "left": "center",
        },
        "legend": {"data": directories},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {"type": "category", "boundaryGap": False, "data": data["dates"]},
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": directory,
                "type": "line",
                "stack": "Total",
                "data": data["directories"][directory]["count"],
            }
            for directory in data["directories"]
        ],
    }
    st_echarts(options=option)
    hierarchy = file_manager.generate_hierarchy()
    data = file_manager.convert_hierarchy_to_list(hierarchy=hierarchy)
    sunburst_option = {
        "title": {"text": "Files in directory", "top": "bottom", "left": "center"},
        "series": {
            "type": "sunburst",
            "data": data,
            "radius": [0, "95%"],
            "sort": None,
            "emphasis": {"focus": "ancestor"},
            "levels": [
                {},
                {
                    "r0": "15%",
                    "r": "35%",
                    "itemStyle": {"borderWidth": 2},
                    "label": {"rotate": "tangential"},
                },
                {"r0": "35%", "r": "70%", "label": {"align": "right"}},
                {
                    "r0": "70%",
                    "r": "72%",
                    "label": {"position": "outside", "padding": 3, "silent": False},
                    "itemStyle": {"borderWidth": 3},
                },
            ],
        },
    }
    st_echarts(options=sunburst_option, height="700px")


def manage_files():
    import streamlit as st

    st.write("# Welcome to File Manager! 👋")
    tree_data = file_manager.get_tree_node_files_structure()
    selected_file = st_ant_tree(
        treeData=tree_data,
        allowClear=True,
        bordered=True,
        filterTreeNode=True,
        multiple=False,
        placeholder="Choose a file",
        showArrow=True,
        showSearch=True,
        treeCheckable=False,
        disabled=False,
        maxTagCount=100,
    )
    if "filters" not in st.session_state:
        st.session_state.filters = {}
    if selected_file:
        if selected_file not in st.session_state.filters:
            st.session_state.filters[selected_file] = {}
        file = file_manager.get_file_from_path(selected_file)
        dt_object = datetime.datetime.fromtimestamp(file.last_modified)
        date_string = dt_object.strftime("%Y-%m-%d")
        st.write(f"**Name:               {file.file_name}**")
        st.write(f"**Size:               {round(file.file_size/(1024*1024), 2)} Mo**")
        st.write(f"**Last update:        {date_string}**")

        condition = st.radio("Condition type", ["AND", "OR"], index=1)
        columns = file.get_columns()
        option = st.selectbox("Select a column", tuple(columns))
        if st.button("Add filter", type="primary"):
            if option not in st.session_state.filters:
                st.session_state.filters[selected_file][option] = []
        updated_filters = st.session_state.filters.copy()
        for filter_key in updated_filters[selected_file]:
            updated_filters[selected_file][filter_key] = st.multiselect(
                f"Select filters for {filter_key}",
                file.get_options(filter_key),
            )
        st.session_state.filters = updated_filters
        st.dataframe(file.filter_data(updated_filters[selected_file], condition))


page_names_to_funcs = {
    "Home page": "home_page",
    "File page": "file_page",
}

page_name = st.sidebar.selectbox("Choose a page", page_names_to_funcs.keys())
if page_name == "Home page":
    intro()
else:
    manage_files()
