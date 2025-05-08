from flask import render_template, request, redirect, url_for, session
import json, zlib, base64
import pycountry
from ..metadata_analysis import fetch_metadata, metadata_recommendations
from ..backlinks import fetch_backlinks, generate_seo_recommendations, generate_seo_insights
from ..traffic import get_traffic_history, traffic_insights
from ..compare_traffic import fetch_traffic_data, generate_llm_comparison_insights
from ..keywords_analysis import fetch_keyword_suggestions
from ..compare_metadata import compare_metadata2, generate_comparison_recommendations
from ..compitator import find_compitators, compare_backlinks
from ..report import create_seo_report
from ..signin import login_route, signup_route
