# Copyright (C) 2011, 2012  Abhijit Mahabal
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>

from farg.core.run_mode.non_interactive import (RunModeNonInteractive, RunMultipleTimes,
                                                MultipleRunGUI)
from farg.third_party import gflags
import sys

FLAGS = gflags.FLAGS

gflags.DEFINE_string('base_flags', '', 'Extra flags for base')
gflags.DEFINE_string('exp_flags', '', 'Extra flags for exp')


class SxSRunMultipleTimes(RunMultipleTimes):
  """Multiple-runner specialized for SxS."""

  def GetSubprocessArguments(self, one_input_spec_arguments):
    arguments = dict(stopping_condition=FLAGS.stopping_condition,
                     stopping_condition_granularity=FLAGS.stopping_condition_granularity,
                     run_mode='single',
                     max_steps=FLAGS.max_steps,
                    )
    arguments.update(one_input_spec_arguments.arguments_dict)
    return arguments

  def RunAll(self):
    for one_input_spec in self.input_spec:
      name = one_input_spec.name
      common_arguments = self.GetSubprocessArguments(one_input_spec)

      for _idx in range(FLAGS.num_iterations):
        left_stats = self.gui.stats.GetLeftStatsFor(name)
        if self.gui.quitting:
          return
        result = RunModeNonInteractive.DoSingleRun(common_arguments, FLAGS.base_flags)
        left_stats.AddData(result)

        right_stats = self.gui.stats.GetRightStatsFor(name)
        if self.gui.quitting:
          return
        result = RunModeNonInteractive.DoSingleRun(common_arguments, FLAGS.exp_flags)
        right_stats.AddData(result)


class RunModeSxS(RunModeNonInteractive):
  def __init__(self, *, controller_class, input_spec):
    print('Initialized SxS run mode')
    if FLAGS.base_flags == FLAGS.exp_flags:
      print('Base and Exp flags are identical (%s). SxS makes no sense!' %
            FLAGS.exp_flags)
      sys.exit(1)
    self.input_spec = input_spec

  def Run(self):
    gui = MultipleRunGUI(input_spec=self.input_spec,
                         multiple_runner_class=SxSRunMultipleTimes,
                         left_name='Base',
                         right_name='Experiment')
    gui.mw.mainloop()
