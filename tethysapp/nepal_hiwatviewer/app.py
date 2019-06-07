from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting

class NepalHiwatviewer(TethysAppBase):
    """
    Tethys app class for Nepal Hiwatviewer.
    """

    name = 'Nepal Hiwatviewer'
    index = 'nepal_hiwatviewer:home'
    icon = 'nepal_hiwatviewer/images/Nepal_Hiwat_Hidroviewer.png'
    package = 'nepal_hiwatviewer'
    root_url = 'nepal-hiwatviewer'
    color = '#006400'
    description = 'Hiwat Hydroviwer for Nepal'
    tags = '&quot;Time Series&quot;'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='nepal-hiwatviewer',
                controller='nepal_hiwatviewer.controllers.home'
            ),
            UrlMap(
                name='get_hiwat',
                url='nepal-hiwatviewer/get-hiwat',
                controller='nepal_hiwatviewer.controllers.get_hiwat'
            ),
            UrlMap(
                name='get_historic',
                url='nepal-hiwatviewer/get-historic',
                controller='nepal_hiwatviewer.controllers.get_historic'
            ),
            UrlMap(
                name='get_hiwat',
                url='nepal-hiwatviewer/download-hiwat',
                controller='nepal_hiwatviewer.controllers.download_hiwat'
            ),
            UrlMap(
                name='get_historic',
                url='nepal-hiwatviewer/download-historic',
                controller='nepal_hiwatviewer.controllers.download_historic'
            ),
            UrlMap(
                name='get-available-dates',
                url='nepal-hiwatviewer/get-available-dates',
                controller='nepal_hiwatviewer.controllers.get_avaialable_dates_raw'
            ),
            UrlMap(
                name='get-return-periods',
                url='nepal-hiwatviewer/get-return-periods',
                controller='nepal_hiwatviewer.controllers.get_return_periods_final'
            ))

        return url_maps

    def custom_settings(self):
        return (

            CustomSetting(
                name='forescast_data',
                type=CustomSetting.TYPE_STRING,
                description='Path to local HIWAT-RAPID forecast directory',
                required=True
            ),
            CustomSetting(
                name='historical_data',
                type=CustomSetting.TYPE_STRING,
                description='Path to local HIWAT-RAPID historical directory',
                required=True
            ),
            CustomSetting(
                name='return_periods',
                type=CustomSetting.TYPE_STRING,
                description='Path to local HIWAT-RAPID historical return periods directory',
                required=True
            ),
            CustomSetting(
                name='Hiwat_Data',
                type=CustomSetting.TYPE_STRING,
                description='Path to local HIWAT data directory',
                required=True
            ),
        )