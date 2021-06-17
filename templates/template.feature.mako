# language: zh-CN
功能: ${name}

% for scenario in scenarios :
% if scenario.tag:
  @${scenario.tag}
% endif
% if len(scenario.get_all_params()) == 0:
  场景: ${scenario.name} 
% else :
  场景大纲: ${scenario.name} 
% endif
  % for i, given_step in enumerate(scenario.given_steps) : 
  	% if i == 0 :
      假如 ${given_step.name} 
    % else :
      而且 ${given_step.name} 
    % endif
  % endfor
  % for j, when_step in enumerate(scenario.when_steps) :
  	% if j == 0 :
      当   ${when_step.name} 
    % else : 
      而且 ${when_step.name} 
    % endif
  % endfor
  % for k, then_step in enumerate(scenario.then_steps) :
  	% if k == 0 :
      那么 ${then_step.name} 
    % else :
      而且 ${then_step.name} 
    % endif
  % endfor

% if len(scenario.get_all_params()) > 0:
      例子:
      ${' | ' + ' | '.join(scenario.get_all_params())} 
      ${' | ' + ' | '.join(scenario.step_data_out)}  
% endif

% endfor

    