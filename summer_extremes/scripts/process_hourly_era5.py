from subprocess import check_call
import click
import xarray as xr
from glob import glob


@click.command()
@click.option('--year', help='Year of data to process', type=click.INT)
def t2m_avg_max_min(year, era5_daily_dir='/home/data/ERA5/day'):

    files = sorted(glob('%s/t2m_hourly_%04i.nc' % (era5_daily_dir, year)))
    if len(files) > 1:  # case of the last year, when the last month is in a different file
        da = []
        for f in files:
            this_da = xr.open_dataarray(f)
            # only keep ERA5 (not ERA5T)
            if 'expver' in this_da.dims:
                this_da = this_da.sel(expver=1)
            da.append(this_da)
        da = xr.concat(da, dim='time')
    else:
        da = xr.open_dataarray(files[0])
        if 'expver' in da.dims:
            da = da.sel(expver=1)

    # calculate daily average
    da_daily_average = da.resample(time='D').mean()
    savedir = '%s/t2m' % era5_daily_dir
    cmd = 'mkdir -p %s' % savedir
    check_call(cmd.split())
    da_daily_average.to_netcdf('%s/t2m_%04i.nc' % (savedir, year))
    del da_daily_average

    # calculate daily max
    da_daily_max = da.resample(time='D').max()
    savedir = '%s/t2m_x' % era5_daily_dir
    cmd = 'mkdir -p %s' % savedir
    check_call(cmd.split())
    da_daily_max.to_netcdf('%s/t2m_x_%04i.nc' % (savedir, year))
    del da_daily_max

    # calculate daily min
    da_daily_min = da.resample(time='D').min()
    savedir = '%s/t2m_n' % era5_daily_dir
    cmd = 'mkdir -p %s' % savedir
    check_call(cmd.split())
    da_daily_min.to_netcdf('%s/t2m_n_%04i.nc' % (savedir, year))
    del da_daily_min

    # delete original file of hourly data
    cmd = 'rm -f %s/t2m_hourly_%04i.nc' % (era5_daily_dir, year)
    check_call(cmd.split())


if __name__ == '__main__':
    t2m_avg_max_min()
