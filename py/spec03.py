import ttm.sm2015 as sm15
import ptools as pt
import numpy as np
plt = pt.plt
import dolfyn.adv.api as avm

doppler_noise = [1.5e-5, 1.5e-5, 0]

eps_freqs = np.array([[.1, 1],
                      [.1, 1],
                      [.1, 3], ])

# 4800 points is 5min at 16hz
binner = avm.TurbBinner(4800, 16)

if 'dat' not in vars():
    dat = sm15.load('TTT_Davit_B', 'pax',
                    bin=True)
    epstmp = np.zeros_like(dat.u)
    Ntmp = 0
    for idx, frq_rng in enumerate(eps_freqs):
        if frq_rng is None:
            continue
        om_rng = frq_rng * 2 * np.pi
        N = ((om_rng[0] < dat.omega) & (dat.omega < om_rng[1])).sum()
        epstmp += binner.calc_epsilon_LT83(dat.Spec[idx] - doppler_noise[idx],
                                           dat.omega,
                                           np.abs(dat.U),
                                           om_rng) * N
        Ntmp += N
    epstmp /= Ntmp
    # epstmp[np.abs(dat.U) < 0.2] = np.NaN
    dat.add_data('epsilon', epstmp, 'main')

pii = 2 * np.pi

vard = dict(
    Spec_umot=dict(color='r', lw=1.5, zorder=1,
                   label=pt.latex['uhead'].spec,
                   noise=np.zeros(3),
    ),
    Spec_uraw=dict(color='k', zorder=2,
                   label=pt.latex['umeas'].spec,
                   noise=[1.5e-4, 1.5e-4, 1.5e-5, ],

    ),
    Spec=dict(color='b', lw=1.5, zorder=3,
              label=pt.latex['ue'].spec,
              noise=[1.5e-4, 1.5e-4, 1.5e-5, ],
    ),
)

with pt.style['onecol']():

    velranges = [(0, 3),
                 ]

    fig, axs = pt.newfig(101, 3, len(velranges),
                         figsize=5,
                         right=0.7, bottom=0.1,
                         sharex=True, sharey=True)
    axs = axs.reshape((3, 1))
    for icol in range(axs.shape[1]):
        vr = velranges[icol]
        umag = np.abs(dat.u)
        inds = (vr[0] < umag) & (umag < vr[1])
        axs[-1, icol].set_xlabel('$f\ \mathrm{[Hz]}$')
        # if vr[0] == 0:
        #     axs[0, icol].set_title(r"$ |\bar{u}| < %0.1f$" % vr[1],
        #                            fontsize='medium')
        # else:
        #     axs[0, icol].set_title(r"$%0.1f < |\bar{u}| < %0.1f$" % vr,
        #                            fontsize='medium')
        axs[0, icol].text(.9, .9, 'N={}'.format(inds.sum()),
                          ha='right', va='top', fontsize='medium',
                          transform=axs[0, icol].transAxes)
        for irow in range(axs.shape[0]):
            # The col-row loop
            ax = axs[irow, icol]
            for fctr in [1, 1e-2, 1e-4, 1e-6, 1e-8]:
                ax.loglog(*pt.powline(factor=fctr), linewidth=0.6,
                          linestyle=':', zorder=-6, color='k')
            for v in ['Spec', 'Spec_umot', 'Spec_uraw', ]:
                # The col-row-var loop
                kwd = vard[v].copy()
                n = kwd.pop('noise')[irow]
                ax.loglog(dat.freq, dat[v][irow, inds].mean(0) * pii - n,
                          **kwd)
    for irow in range(axs.shape[0]):
        # The col-only loop
        axs[irow, 0].set_ylabel('$\mathrm{[m^2s^{-2}/Hz]}$')
        axs[irow, -1].text(1.04, 0.05, '$%s$' % (pt.vel_comps[irow]),
                           ha='left', va='bottom', fontsize='x-large',
                           transform=axs[irow, -1].transAxes, clip_on=False)
        #                    ha='left', va='bottom', fontsize='medium',
        #                    transform=axs[irow, -1].transAxes, clip_on=False)

    axs[0, -1].legend(loc='upper left', bbox_to_anchor=[1.02, 1.0],
                      handlelength=1.4, handletextpad=0.4,
                      prop=dict(size='medium'))
    ax.set_ylim((1e-4, 10))
    ax.set_xlim((1e-3, 5))

    fig.savefig(pt.figdir + 'SpecFig03_TTT.pdf')

